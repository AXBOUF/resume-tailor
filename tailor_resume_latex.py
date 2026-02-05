#!/usr/bin/env python3
"""
Tool 3 v2: LaTeX Resume Tailor
Input: 
  - Parsed resume JSON (from Tool 1)
  - Job descriptions JSON (from Tool 2)
Output: Tailored PDF resumes (Jake's Resume format)

Usage:
  python3 tailor_resume_latex.py <resume_json> <jobs_json> [output_dir]

Example:
  python3 tailor_resume_latex.py resume_parsed.json jobs_scraped_v2.json ./output
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.tailor_engine import ResumeTailor
from src.latex_generator import JakeResumeLaTeXGenerator
from src.config import GROQ_API_KEY


class LaTeXResumeTailor:
    """Tailor resume and generate LaTeX/PDF output"""
    
    def __init__(self):
        self.tailor = ResumeTailor()
        self.latex_gen = JakeResumeLaTeXGenerator()
    
    def tailor_for_job(self, resume_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """
        Tailor resume for a specific job and return structured data
        """
        # Create tailored content using LLM
        prompt = self._create_tailoring_prompt(resume_data, job_data)
        
        try:
            # Get tailored content from LLM
            tailored_text = self.tailor.tailor_resume(resume_data, job_data)
            
            # Parse the tailored content into structured format
            structured_data = self._parse_tailored_content(
                tailored_text, 
                resume_data, 
                job_data
            )
            
            return structured_data
            
        except Exception as e:
            print(f"   ⚠️  LLM tailoring failed: {e}")
            print("   📝 Using original resume with minor adjustments...")
            return self._fallback_tailoring(resume_data, job_data)
    
    def _create_tailoring_prompt(self, resume_data: Dict, job_data: Dict) -> str:
        """Create prompt for tailoring resume"""
        
        # Extract relevant info
        contact = resume_data.get('contact_info', {})
        sections = resume_data.get('sections', {})
        
        # Build resume text
        resume_text = self._build_resume_text(resume_data)
        
        prompt = f"""You are an expert resume writer specializing in Jake's Resume format - a popular, ATS-optimized LaTeX template used in the tech industry.

YOUR TASK: Tailor the following resume for the job position below. Maintain TRUTHFULNESS - do not invent experience, only rephrase and highlight existing qualifications.

JOB POSITION:
Title: {job_data.get('title', 'Position')}
Company: {job_data.get('company', 'Company')}
Description: {job_data.get('description', '')[:2000]}

CANDIDATE RESUME:
{resume_text}

INSTRUCTIONS:
1. Tailor the resume content to match the job requirements
2. Use action verbs and quantify achievements where possible
3. Prioritize relevant experience and skills
4. Convert experience descriptions to 3-5 impactful bullet points per role
5. Categorize skills into: Languages, Frameworks, Developer Tools, Libraries
6. Include relevant projects that demonstrate job-specific skills
7. Maintain the Jake's Resume structure:
   - Heading (Name, Contact)
   - Education
   - Experience (with bullet points)
   - Projects (if relevant)
   - Technical Skills

OUTPUT FORMAT - Return ONLY a JSON object:
{{
  "heading": {{
    "name": "Full Name",
    "phone": "phone number",
    "email": "email",
    "linkedin": "linkedin URL",
    "portfolio": "github/portfolio URL"
  }},
  "education": [
    {{
      "school": "University Name",
      "location": "Location",
      "degree": "Degree Name",
      "dates": "Dates"
    }}
  ],
  "experience": [
    {{
      "company": "Company Name",
      "location": "Location", 
      "title": "Job Title",
      "dates": "Employment Dates",
      "bullets": [
        "Achievement bullet 1 with metrics",
        "Achievement bullet 2",
        "Achievement bullet 3"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "tech_stack": "Python, React, SQL",
      "bullets": [
        "What the project does",
        "Your contribution and impact"
      ]
    }}
  ],
  "skills": {{
    "languages": "Python, SQL, JavaScript",
    "frameworks": "React, Flask, FastAPI",
    "developer_tools": "Git, Docker, AWS",
    "libraries": "pandas, NumPy, scikit-learn"
  }}
}}

IMPORTANT:

IMPORTANT:
- Return ONLY valid JSON, no markdown formatting
- Use double quotes for all strings
- Ensure all brackets and braces match
- Do not include any explanatory text
"""
        return prompt
    
    def _build_resume_text(self, resume_data: Dict) -> str:
        """Build plain text from resume data for the prompt"""
        lines = []
        
        # Contact info
        contact = resume_data.get('contact_info', {})
        if contact.get('name'):
            lines.append(f"Name: {contact['name']}")
        if contact.get('email'):
            lines.append(f"Email: {contact['email']}")
        if contact.get('phone'):
            lines.append(f"Phone: {contact['phone']}")
        
        lines.append("")
        
        # Sections
        sections = resume_data.get('sections', {})
        for section_name, content in sections.items():
            if content:
                lines.append(f"\n{section_name.upper()}:")
                if isinstance(content, list):
                    for line in content:
                        lines.append(line)
                else:
                    lines.append(str(content))
        
        return '\n'.join(lines)
    
    def _parse_tailored_content(self, tailored_text: str, original_data: Dict, job_data: Dict) -> Dict:
        """Parse LLM output into structured format"""
        
        # Try to extract JSON from the response
        try:
            # Look for JSON block
            json_start = tailored_text.find('{')
            json_end = tailored_text.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = tailored_text[json_start:json_end+1]
                data = json.loads(json_str)
                
                # Validate structure
                if 'heading' in data and 'experience' in data:
                    return data
        except:
            pass
        
        # Fallback: use original data with job title
        return self._fallback_tailoring(original_data, job_data)
    
    def _fallback_tailoring(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Fallback if LLM fails - use original with minor adjustments"""
        
        contact = resume_data.get('contact_info', {})
        sections = resume_data.get('sections', {})
        
        # Build structured data from original
        structured = {
            'heading': {
                'name': contact.get('name', ''),
                'phone': contact.get('phone', ''),
                'email': contact.get('email', ''),
                'linkedin': contact.get('linkedin', ''),
                'portfolio': contact.get('portfolio', contact.get('github', ''))
            },
            'education': [],
            'experience': [],
            'projects': [],
            'skills': {
                'languages': '',
                'frameworks': '',
                'developer_tools': '',
                'libraries': ''
            }
        }
        
        # Parse education
        edu_content = sections.get('education', [])
        if edu_content:
            structured['education'].append({
                'school': edu_content[0] if edu_content else 'University',
                'location': '',
                'degree': edu_content[1] if len(edu_content) > 1 else 'Degree',
                'dates': ''
            })
        
        # Parse experience (convert to bullets)
        exp_content = sections.get('experience', [])
        if exp_content:
            exp_text = '\n'.join(exp_content)
            bullets = self._text_to_bullets(exp_text)
            
            structured['experience'].append({
                'company': 'Company',
                'location': '',
                'title': 'Position',
                'dates': '',
                'bullets': bullets[:5] if bullets else ['Experience description']
            })
        
        # Parse skills
        skills_content = sections.get('skills', [])
        if skills_content:
            skills_text = ' '.join(skills_content)
            structured['skills']['languages'] = skills_text
        
        return structured
    
    def _text_to_bullets(self, text: str) -> List[str]:
        """Convert text to bullet points"""
        import re
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only substantial sentences
                bullets.append(sentence)
        
        return bullets[:5]  # Max 5 bullets
    
    def generate_latex(self, structured_data: Dict) -> str:
        """Generate LaTeX from structured data"""
        return self.latex_gen.generate_full_resume(structured_data)
    
    def compile_pdf(self, tex_file: str, output_dir: str) -> bool:
        """Compile LaTeX to PDF"""
        try:
            # Change to output directory
            original_dir = os.getcwd()
            os.chdir(output_dir)
            
            # Run pdflatex twice for references
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            os.chdir(original_dir)
            
            # Check if PDF was created
            pdf_file = tex_file.replace('.tex', '.pdf')
            return os.path.exists(os.path.join(output_dir, pdf_file))
            
        except FileNotFoundError:
            print("   ⚠️  pdflatex not found. Install texlive or use Overleaf.")
            return False
        except Exception as e:
            print(f"   ⚠️  PDF compilation failed: {e}")
            return False


def generate_filename(contact_name: str, job_title: str, company: str) -> str:
    """Generate professional filename"""
    # Clean up inputs
    name = contact_name.replace(' ', '_') if contact_name else 'Resume'
    role = job_title.replace(' ', '_') if job_title else 'Position'
    comp = company.replace(' ', '_') if company else 'Company'
    
    # Limit lengths
    name = name[:20]
    role = role[:30]
    comp = comp[:20]
    
    return f"{name}_{role}_{comp}"


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Resume Tailor - LaTeX Edition")
        print("Generates Jake's Resume formatted PDFs")
        print("\nUsage:")
        print("  python3 tailor_resume_latex.py <resume_json> <jobs_json> [output_dir]")
        print("\nExamples:")
        print("  python3 tailor_resume_latex.py resume.json jobs.json")
        print("  python3 tailor_resume_latex.py resume.json jobs.json ./my_resumes")
        print("\nPrerequisites:")
        print("  1. Run parse_resume.py to create resume JSON")
        print("  2. Run scrape_jobs_v2.py to create jobs JSON")
        print("  3. Set GROQ_API_KEY in .env file")
        print("  4. Optional: Install texlive for local PDF compilation")
        sys.exit(1)
    
    resume_file = sys.argv[1]
    jobs_file = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else './output'
    
    # Check API key
    if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
        print("❌ Error: GROQ_API_KEY not configured")
        print("   Create .env file with: GROQ_API_KEY=your_key_here")
        print("   Get free key: https://console.groq.com/keys")
        sys.exit(1)
    
    # Load data
    print(f"📄 Loading resume: {resume_file}")
    with open(resume_file, 'r') as f:
        resume_data = json.load(f)
    
    print(f"💼 Loading jobs: {jobs_file}")
    with open(jobs_file, 'r') as f:
        jobs_data = json.load(f)
    
    # Extract jobs list
    if isinstance(jobs_data, dict):
        jobs = jobs_data.get('jobs', [])
    else:
        jobs = jobs_data
    
    if not jobs:
        print("❌ Error: No jobs found in jobs file")
        sys.exit(1)
    
    print(f"\n🎯 Processing {len(jobs)} job(s)...")
    print(f"👤 Candidate: {resume_data.get('contact_info', {}).get('name', 'Unknown')}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize tailor
    tailor = LaTeXResumeTailor()
    
    results = []
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] Tailoring for: {job.get('title', 'Unknown')} @ {job.get('company', 'Unknown')}")
        
        try:
            # Tailor resume
            print("   📝 Using AI to tailor content...")
            structured_data = tailor.tailor_for_job(resume_data, job)
            
            # Generate LaTeX
            print("   📄 Generating LaTeX...")
            latex_content = tailor.generate_latex(structured_data)
            
            # Generate filename
            filename_base = generate_filename(
                structured_data['heading'].get('name', ''),
                job.get('title', ''),
                job.get('company', '')
            )
            
            # Save LaTeX
            tex_file = os.path.join(output_dir, f"{filename_base}.tex")
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            print(f"   ✅ LaTeX saved: {filename_base}.tex")
            
            # Try to compile PDF
            print("   🔄 Attempting PDF compilation...")
            pdf_success = tailor.compile_pdf(f"{filename_base}.tex", output_dir)
            
            if pdf_success:
                print(f"   ✅ PDF created: {filename_base}.pdf")
            else:
                print(f"   ⚠️  PDF compilation skipped")
                print(f"      To compile manually:")
                print(f"      1. Go to overleaf.com")
                print(f"      2. Upload: {tex_file}")
                print(f"      3. Recompile")
            
            results.append({
                'job': job,
                'filename': filename_base,
                'tex_file': tex_file,
                'pdf_created': pdf_success,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'job': job,
                'error': str(e),
                'success': False
            })
    
    # Save summary
    summary_file = os.path.join(output_dir, "tailoring_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'input_resume': resume_file,
            'input_jobs': jobs_file,
            'output_directory': output_dir,
            'total_jobs': len(jobs),
            'successful': sum(1 for r in results if r['success']),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "="*70)
    print(f"✅ Tailoring complete!")
    print(f"\n📊 Summary:")
    print(f"   Total jobs: {len(jobs)}")
    print(f"   Successful: {sum(1 for r in results if r['success'])}")
    print(f"   PDFs created: {sum(1 for r in results if r.get('pdf_created'))}")
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📝 Summary: {summary_file}")
    
    # List created files
    print(f"\n📄 Generated files:")
    for r in results:
        if r['success']:
            print(f"   - {r['filename']}.tex")
            if r.get('pdf_created'):
                print(f"   - {r['filename']}.pdf")


if __name__ == "__main__":
    main()