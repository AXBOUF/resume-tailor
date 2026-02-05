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
        self.min_request_interval = 60.0 / MAX_REQUESTS_PER_MINUTE  # Seconds between requests
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def tailor_resume(self, resume_data: Dict[str, Any], job_data: Dict[str, str]) -> str:
        """
        Tailor resume for a specific job
        Returns the tailored resume text
        """
        self._rate_limit()
        
        # Prepare the resume text
        resume_text = self._format_resume_for_prompt(resume_data)
        
        # Create the prompt
        prompt = self._create_tailoring_prompt(resume_text, job_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert resume writer and career coach specializing in ATS-optimized resumes. 
Your task is to tailor resumes for specific job descriptions while maintaining complete truthfulness.

Key principles:
1. NEVER fabricate experience, skills, or qualifications
2. Emphasize existing relevant experience by rephrasing and highlighting
3. Use keywords from the job description naturally
4. Quantify achievements where possible
5. Maintain professional formatting
6. Keep the resume to 1-2 pages
7. Ensure the resume passes ATS screening

Format the output as a complete, formatted resume with clear sections."""
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
        """Format resume data for the LLM prompt"""
        sections = resume_data.get('sections', {})
        contact = resume_data.get('contact_info', {})
        
        formatted = []
        
        # Contact info
        if contact.get('name'):
            formatted.append(f"NAME: {contact['name']}")
        if contact.get('email'):
            formatted.append(f"EMAIL: {contact['email']}")
        if contact.get('phone'):
            formatted.append(f"PHONE: {contact['phone']}")
        if contact.get('linkedin'):
            formatted.append(f"LINKEDIN: {contact['linkedin']}")
        if contact.get('portfolio'):
            formatted.append(f"PORTFOLIO: {contact['portfolio']}")
        
        formatted.append("")
        
        # Sections
        for section_name, content in sections.items():
            if content:
                formatted.append(f"\n{section_name.upper()}:")
                for line in content:
                    formatted.append(line)
        
        # If no structured sections, use raw text
        if not any(sections.values()):
            formatted.append("\nRAW RESUME TEXT:")
            formatted.append(resume_data.get('raw_text', ''))
        
        return '\n'.join(formatted)
    
    def _create_tailoring_prompt(self, resume_text: str, job_data: Dict[str, str]) -> str:
        """Create the prompt for resume tailoring"""
        
        prompt = f"""Please tailor the following resume for this specific job position.

JOB DETAILS:
- Title: {job_data.get('title', 'Not specified')}
- Company: {job_data.get('company', 'Not specified')}

JOB DESCRIPTION:
{job_data.get('description', 'No description available')}

ORIGINAL RESUME:
{resume_text}

INSTRUCTIONS:
1. Analyze the job description for key requirements, skills, and qualifications
2. Review the original resume and identify matching experience
3. Tailor the resume by:
   - Reordering bullet points to prioritize relevant experience
   - Rewording descriptions to use job-specific keywords
   - Quantifying achievements where relevant
   - Highlighting transferable skills
   - Adjusting the professional summary (if present) to match the role
   - Ensuring all claimed skills/experience are truthful and from the original resume

4. Maintain professional resume formatting with these sections:
   - Contact Information
   - Professional Summary (tailored to job)
   - Work Experience (prioritized and reworded)
   - Skills (reorganized and keyword-optimized)
   - Education
   - Certifications/Projects (if relevant)

5. Output the complete tailored resume in a clean, professional format.

Please provide the tailored resume now:"""

        return prompt
    
    def batch_tailor(self, resume_data: Dict[str, Any], jobs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Tailor resume for multiple jobs with progress tracking"""
        results = []
        
        for i, job in enumerate(jobs, 1):
            try:
                tailored_text = self.tailor_resume(resume_data, job)
                results.append({
                    'job': job,
                    'tailored_resume': tailored_text,
                    'success': True,
                    'index': i
                })
            except Exception as e:
                results.append({
                    'job': job,
                    'tailored_resume': '',
                    'success': False,
                    'error': str(e),
                    'index': i
                })
        
        return results
    
    def extract_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description"""
        self._rate_limit()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the most important technical skills, soft skills, and qualifications from job descriptions. Return only a comma-separated list."
                    },
                    {
                        "role": "user",
                        "content": f"Extract the top 15-20 most important keywords (skills, technologies, qualifications) from this job description:\n\n{job_description}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            keywords_text = response.choices[0].message.content
            # Parse comma-separated list
            keywords = [k.strip() for k in keywords_text.split(',')]
            return keywords
            
        except Exception as e:
            print(f"Warning: Could not extract keywords: {e}")
            return []