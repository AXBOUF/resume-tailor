#!/usr/bin/env python3
"""
Tool 3: Resume Tailor
Input: 
  - Parsed resume JSON (from Tool 1)
  - Job descriptions JSON (from Tool 2)
Output: Tailored resume files (DOCX and PDF)

Usage:
  python3 tailor_resume.py <resume_json> <jobs_json> [output_dir]

Example:
  python3 tailor_resume.py resume_parsed.json jobs_scraped.json ./output

NOTE: If using virtual environment (venv), activate it first:
  source venv/bin/activate
  python3 tailor_resume.py ...
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.tailor_engine import ResumeTailor
from src.output_generator import ResumeGenerator
from src.config import OUTPUT_DIR

def load_json(file_path):
    """Load JSON file"""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)

def tailor_resume(resume_json_path, jobs_json_path, output_dir=None):
    """Tailor resume for each job"""
    
    # Load data
    print(f"📄 Loading resume data from: {resume_json_path}")
    resume_data = load_json(resume_json_path)
    
    print(f"💼 Loading job data from: {jobs_json_path}")
    jobs_data = load_json(jobs_json_path)
    
    # Extract jobs array
    if isinstance(jobs_data, dict) and 'jobs' in jobs_data:
        jobs = jobs_data['jobs']
    elif isinstance(jobs_data, list):
        jobs = jobs_data
    else:
        print("❌ Error: Invalid jobs JSON structure")
        sys.exit(1)
    
    print(f"\n📊 Processing {len(jobs)} job(s)...")
    print(f"👤 Candidate: {resume_data.get('contact_info', {}).get('name', 'Unknown')}")
    
    # Set output directory
    if not output_dir:
        output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize tools
    tailor = ResumeTailor()
    generator = ResumeGenerator()
    generator.output_dir = output_dir
    
    results = []
    successful = 0
    failed = 0
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] Tailoring for: {job['title']} at {job['company']}")
        
        try:
            # Check if job has valid description
            if len(job['description']) < 100:
                print(f"   ⚠️  Warning: Short job description ({len(job['description'])} chars)")
            
            # Tailor the resume
            print(f"   📝 Sending to LLM for tailoring...")
            tailored_text = tailor.tailor_resume(resume_data, job)
            
            # Generate output files
            base_filename = f"resume_{i:02d}_{job['company'][:20].replace(' ', '_')}"
            files = generator.generate_both_formats(tailored_text, job, base_filename)
            
            results.append({
                'job': job,
                'tailored_text': tailored_text,
                'files': files,
                'success': True
            })
            
            successful += 1
            print(f"   ✅ Success! Generated:")
            print(f"      📄 {files['docx_name']}")
            print(f"      📑 {files['pdf_name']}")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results.append({
                'job': job,
                'error': str(e),
                'success': False
            })
            failed += 1
    
    # Save results summary
    summary_file = os.path.join(output_dir, "tailoring_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'input_resume': resume_json_path,
            'input_jobs': jobs_json_path,
            'total_jobs': len(jobs),
            'successful': successful,
            'failed': failed,
            'output_directory': output_dir,
            'results': [
                {
                    'job': r['job'],
                    'success': r['success'],
                    'files': r.get('files', {}),
                    'error': r.get('error', None)
                }
                for r in results
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "="*60)
    print(f"✅ Tailoring complete!")
    print(f"\n📊 Summary:")
    print(f"   Total jobs: {len(jobs)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"\n📁 Output directory: {output_dir}")
    print(f"📝 Summary saved to: {summary_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 tailor_resume.py <resume_json> <jobs_json> [output_dir]")
        print("\nExamples:")
        print("  python3 tailor_resume.py resume_parsed.json jobs_scraped.json")
        print("  python3 tailor_resume.py my_resume.json jobs.json ./my_output")
        print("\nPrerequisites:")
        print("  1. Run parse_resume.py to create resume JSON")
        print("  2. Run scrape_jobs.py to create jobs JSON")
        print("  3. Set GROQ_API_KEY in .env file")
        sys.exit(1)
    
    resume_json = sys.argv[1]
    jobs_json = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    tailor_resume(resume_json, jobs_json, output_dir)