from groq import Groq
import time
from typing import Dict, List, Any
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE, MAX_REQUESTS_PER_MINUTE


class ResumeTailor:
    """Use LLM to tailor resumes for specific job descriptions"""

    def __init__(self):
        if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
            raise ValueError("Groq API key not configured. Please set GROQ_API_KEY in .env file")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.last_request_time = 0
        self.min_request_interval = 60.0 / MAX_REQUESTS_PER_MINUTE

    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def tailor_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, str]) -> str:
        self._rate_limit()
        resume_text = self._format_resume_for_prompt(resume_data)
        prompt = self._create_tailoring_prompt(resume_text, job_data)

        # Guard: job description must be actual text, not a URL
        description = job_data.get('description', '')
        if description.strip().startswith('http') or len(description.strip()) < 100:
            raise ValueError(
                f"Job description for '{job_data.get('title')} at {job_data.get('company')}' "
                f"appears to be a URL or is too short ({len(description)} chars). "
                f"scrape_jobs.py may have failed to extract the job description text. "
                f"Value: {description[:200]!r}"
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert resume writer specializing in ATS-optimized resumes "
                            "following Jake's Resume format. Your output will be parsed by a program "
                            "that identifies sections by their exact header names, so you MUST use "
                            "these exact section headers (on their own line, followed by nothing):\n\n"
                            "  SUMMARY\n"
                            "  EXPERIENCE\n"
                            "  EDUCATION\n"
                            "  TECHNICAL SKILLS\n"
                            "  PROJECTS\n"
                            "  CERTIFICATIONS\n\n"
                            "Formatting rules:\n"
                            "1. NEVER fabricate experience, skills, or qualifications.\n"
                            "2. Contact line format: Name on first line, then one line with: "
                            "phone | email | linkedin.com/in/handle | github.com/handle\n"
                            "3. Experience entries MUST follow this exact pattern (one entry per job):\n"
                            "   Company Name | Job Title | Month Year - Month Year | City, State\n"
                            "   • Bullet point achievement (start with strong action verb, quantify impact)\n"
                            "   • Bullet point achievement\n"
                            "4. Skills MUST be grouped with a category label:\n"
                            "   Languages: Python, Java, SQL\n"
                            "   Frameworks: React, Django\n"
                            "5. Use bullet character for ALL bullet points.\n"
                            "6. Keep to 1 page if under 5 years experience, 2 pages otherwise.\n"
                            "7. Do NOT add any markdown, asterisks for bold, or extra symbols."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error tailoring resume: {str(e)}")

    def _format_resume_for_prompt(self, resume_data: Dict[str, Any]) -> str:
        sections = resume_data.get('sections', {})
        contact  = resume_data.get('contact_info', {})
        formatted = []

        if contact.get('name'):      formatted.append(f"NAME: {contact['name']}")
        if contact.get('email'):     formatted.append(f"EMAIL: {contact['email']}")
        if contact.get('phone'):     formatted.append(f"PHONE: {contact['phone']}")
        if contact.get('linkedin'):  formatted.append(f"LINKEDIN: {contact['linkedin']}")
        if contact.get('portfolio'): formatted.append(f"PORTFOLIO: {contact['portfolio']}")
        formatted.append("")

        for section_name, content in sections.items():
            if content:
                formatted.append(f"\n{section_name.upper()}:")
                for line in content:
                    formatted.append(line)

        if not any(sections.values()):
            formatted.append("\nRAW RESUME TEXT:")
            formatted.append(resume_data.get('raw_text', ''))

        return '\n'.join(formatted)

    def _create_tailoring_prompt(self, resume_text: str, job_data: Dict[str, str]) -> str:
        return f"""Tailor the resume below for the following job. Output a complete, clean resume.

JOB DETAILS:
Title: {job_data.get('title', 'Not specified')}
Company: {job_data.get('company', 'Not specified')}

JOB DESCRIPTION:
{job_data.get('description', 'No description available')}

ORIGINAL RESUME:
{resume_text}

OUTPUT INSTRUCTIONS:
Produce the tailored resume using ONLY the exact section headers listed in your instructions.
Structure every job in EXPERIENCE as:
  Company Name | Job Title | Month Year - Month Year | Location
  - bullet (action verb + metric)

Structure TECHNICAL SKILLS as labeled categories:
  Category: item1, item2, item3

Do not include any commentary, explanation, or markdown formatting outside the resume itself.
Begin the output with the candidate's name on the first line."""

    def batch_tailor(self, resume_data: Dict[str, Any], jobs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        results = []
        for i, job in enumerate(jobs, 1):
            try:
                tailored_text = self.tailor_resume(resume_data, job)
                results.append({'job': job, 'tailored_resume': tailored_text, 'success': True, 'index': i})
            except Exception as e:
                results.append({'job': job, 'tailored_resume': '', 'success': False, 'error': str(e), 'index': i})
        return results

    def extract_keywords(self, job_description: str) -> List[str]:
        self._rate_limit()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the most important technical skills, soft skills, and qualifications from job descriptions. Return only a comma-separated list."},
                    {"role": "user",   "content": f"Extract the top 15-20 most important keywords from this job description:\n\n{job_description}"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return [k.strip() for k in response.choices[0].message.content.split(',')]
        except Exception as e:
            print(f"Warning: Could not extract keywords: {e}")
            return []
