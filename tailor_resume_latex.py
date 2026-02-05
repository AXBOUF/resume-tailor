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
import re
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
    
    def _extract_contact_info(self, contact: Dict) -> Dict:
        """Extract clean contact info from parsed data"""
        name = contact.get('name', '')
        phone = contact.get('phone', '')
        email = contact.get('email', '')
        linkedin = contact.get('linkedin', '')
        portfolio = contact.get('portfolio', contact.get('github', ''))
        
        # Check if linkedin/portfolio fields contain combined contact info
        combined_info = linkedin if len(linkedin) > 50 else portfolio
        
        if combined_info and '|' in combined_info:
            # Parse combined contact line
            parts = [p.strip() for p in combined_info.split('|')]
            
            for part in parts:
                if '@' in part and not email:
                    email = part
                elif part.startswith('+') or part.replace('-', '').replace(' ', '').isdigit():
                    if not phone:
                        phone = part
                elif 'linkedin' in part.lower():
                    linkedin = part
                elif 'github' in part.lower() or 'portfolio' in part.lower():
                    portfolio = part
        
        return {
            'name': name,
            'phone': phone,
            'email': email,
            'linkedin': linkedin,
            'portfolio': portfolio
        }
    
    def _fallback_tailoring(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Fallback if LLM fails - use original with minor adjustments"""
        
        contact = resume_data.get('contact_info', {})
        sections = resume_data.get('sections', {})
        
        # Extract clean contact info
        clean_contact = self._extract_contact_info(contact)
        
        # Build structured data from original
        structured = {
            'heading': clean_contact,
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
            # Try to extract company and title from first lines
            company = 'Company'
            title = 'Position'
            dates = ''
            
            # First line often contains company/title info
            if exp_content:
                first_line = exp_content[0]
                # Try to parse common formats
                if ' at ' in first_line.lower():
                    parts = first_line.split(' at ', 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                elif ',' in first_line:
                    parts = first_line.split(',', 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title = first_line.strip()
            
            # Get bullet points (skip first line if it was header)
            content_start = 1 if len(exp_content) > 1 else 0
            exp_text = '\n'.join(exp_content[content_start:])
            bullets = self._text_to_bullets(exp_text)
            
            if not bullets and exp_content:
                bullets = [exp_content[0]]
            
            structured['experience'].append({
                'company': company,
                'location': '',
                'title': title,
                'dates': dates,
                'bullets': bullets[:5] if bullets else ['Experience description']
            })
        
        # Parse skills - try to categorize them
        skills_content = sections.get('skills', [])
        if skills_content:
            skills_text = ' '.join(skills_content)
            
            # Remove common labels that might already be in the text
            skills_text = skills_text.replace('Languages:', '').replace('Languages', '', 1)
            skills_text = skills_text.replace('Skills:', '').replace('Skills', '', 1)
            skills_text = skills_text.strip()
            
            # Simple categorization
            languages = []
            frameworks = []
            tools = []
            libraries = []
            
            # Common keywords for categorization
            lang_keywords = ['Python', 'SQL', 'JavaScript', 'Java', 'R', 'C++', 'C#', 'Go', 'Ruby', 'PHP']
            framework_keywords = ['React', 'Flask', 'FastAPI', 'Django', 'Node.js', 'Angular', 'Vue']
            tool_keywords = ['Git', 'Docker', 'AWS', 'Azure', 'GCP', 'Kubernetes', 'Jenkins']
            lib_keywords = ['pandas', 'NumPy', 'Matplotlib', 'scikit-learn', 'TensorFlow', 'PyTorch']
            
            # Split by common delimiters
            all_skills = re.split(r'[,;/|•\-]', skills_text)
            
            for skill in all_skills:
                skill = skill.strip()
                if not skill:
                    continue
                
                # Categorize
                if any(kw in skill for kw in lang_keywords):
                    languages.append(skill)
                elif any(kw in skill for kw in framework_keywords):
                    frameworks.append(skill)
                elif any(kw in skill for kw in tool_keywords):
                    tools.append(skill)
                elif any(kw in skill for kw in lib_keywords):
                    libraries.append(skill)
                else:
                    # Default to languages
                    languages.append(skill)
            
            structured['skills']['languages'] = ', '.join(languages) if languages else skills_text
            structured['skills']['frameworks'] = ', '.join(frameworks)
            structured['skills']['developer_tools'] = ', '.join(tools)
            structured['skills']['libraries'] = ', '.join(libraries)
        
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
    
    def compile_pdf(self, tex_file: str, output_dir: str, use_docker: bool = True) -> bool:
        """Compile LaTeX to PDF using Docker or local pdflatex"""
        
        # Try Docker first if enabled
        if use_docker and self._docker_available():
            return self._compile_with_docker(tex_file, output_dir)
        
        # Fall back to local pdflatex
        return self._compile_with_pdflatex(tex_file, output_dir)
    
    def _docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _compile_with_docker(self, tex_file: str, output_dir: str) -> bool:
        """Compile LaTeX using Docker"""
        try:
            basename = os.path.basename(tex_file)
            
            print(f"   🐳 Using Docker for PDF compilation...")
            
            # Run pdflatex twice in Docker
            for i in range(2):
                result = subprocess.run(
                    [
                        'docker', 'run', '--rm',
                        '-v', f'{os.path.abspath(output_dir)}:/workdir',
                        '-w', '/workdir',
                        'texlive/texlive:latest',
                        'pdflatex',
                        '-interaction=nonstopmode',
                        basename
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0 and i == 1:  # Only show error on second run
                    # Check if PDF was still created (warnings are OK)
                    pass
            
            # Check if PDF was created
            pdf_file = tex_file.replace('.tex', '.pdf')
            success = os.path.exists(pdf_file)
            
            if success:
                print(f"   ✅ PDF compiled successfully with Docker")
            
            return success
            
        except Exception as e:
            print(f"   ⚠️  Docker compilation failed: {e}")
            print(f"   📝 Falling back to local pdflatex...")
            return self._compile_with_pdflatex(tex_file, output_dir)
    
    def _compile_with_pdflatex(self, tex_file: str, output_dir: str) -> bool:
        """Compile LaTeX using local pdflatex"""
        try:
            # Change to output directory
            original_dir = os.getcwd()
            os.chdir(output_dir)
            
            tex_basename = os.path.basename(tex_file)
            
            # Run pdflatex twice for references
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_basename],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            os.chdir(original_dir)
            
            # Check if PDF was created
            pdf_file = tex_file.replace('.tex', '.pdf')
            success = os.path.exists(pdf_file)
            
            if success:
                print(f"   ✅ PDF compiled successfully with local pdflatex")
            
            return success
            
        except FileNotFoundError:
            print("   ⚠️  pdflatex not found locally and Docker failed/unavailable")
            print("   💡 Options:")
            print("      1. Install texlive: sudo pacman -S texlive-most")
            print("      2. Use Docker: ./docker-run.sh compile")
            print("      3. Upload .tex to Overleaf: https://www.overleaf.com")
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
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate tailored resumes using Jake\'s Resume LaTeX format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tailor_resume_latex.py resume.json jobs.json
  python3 tailor_resume_latex.py resume.json jobs.json ./my_output --no-docker
  python3 tailor_resume_latex.py resume.json jobs.json --skip-pdf

Prerequisites:
  1. Run parse_resume.py to create resume JSON
  2. Run scrape_jobs_v2.py to create jobs JSON  
  3. Set GROQ_API_KEY in .env file
  4. For PDF: Install texlive OR use Docker OR upload to Overleaf
        """
    )
    
    parser.add_argument('resume_json', help='Path to parsed resume JSON file')
    parser.add_argument('jobs_json', help='Path to jobs JSON file')
    parser.add_argument('output_dir', nargs='?', default='./output', 
                       help='Output directory (default: ./output)')
    parser.add_argument('--no-docker', action='store_true',
                       help='Disable Docker, use local pdflatex only')
    parser.add_argument('--skip-pdf', action='store_true',
                       help='Generate .tex files only, skip PDF compilation')
    parser.add_argument('--docker-image', default='texlive/texlive:latest',
                       help='Docker image for LaTeX compilation (default: texlive/texlive:latest)')
    
    args = parser.parse_args()
    
    resume_file = args.resume_json
    jobs_file = args.jobs_json
    output_dir = args.output_dir
    use_docker = not args.no_docker
    skip_pdf = args.skip_pdf
    
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
            if skip_pdf:
                print("   ⏭️  PDF compilation skipped (--skip-pdf)")
                pdf_success = False
            else:
                print("   🔄 Attempting PDF compilation...")
                pdf_success = tailor.compile_pdf(tex_file, output_dir, use_docker=use_docker)
                
                if pdf_success:
                    print(f"   ✅ PDF created: {filename_base}.pdf")
                else:
                    print(f"   ⚠️  PDF compilation failed")
                    print(f"      To compile manually:")
                    print(f"      1. Install texlive: sudo pacman -S texlive-most")
                    print(f"      2. Use Docker: docker run --rm -v $(pwd)/{output_dir}:/workdir texlive/texlive:latest pdflatex {filename_base}.tex")
                    print(f"      3. Upload to Overleaf: https://www.overleaf.com")
            
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