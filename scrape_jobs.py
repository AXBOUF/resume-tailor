#!/usr/bin/env python3
"""
Tool 2: Job Scraper
Input: URLs of job postings (one or multiple)
Output: JSON file with job descriptions

Usage: 
  python3 scrape_jobs.py <url1> [url2] [url3] ... [output.json]
  
Or create a text file with URLs (one per line):
  python3 scrape_jobs.py --file urls.txt [output.json]

NOTE: If using virtual environment (venv), activate it first:
  source venv/bin/activate
  python3 scrape_jobs.py ...
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.job_scraper import JobScraper
from src.tailor_engine import ResumeTailor

def scrape_single_job(url, use_llm_extraction=False):
    """Scrape a single job URL"""
    print(f"\n🔍 Scraping: {url}")
    
    scraper = JobScraper()
    job_data = scraper.scrape_job(url)
    
    # If description is too short and LLM extraction is enabled
    if use_llm_extraction and len(job_data['description']) < 500:
        print(f"   ⚠️  Short description ({len(job_data['description'])} chars), attempting LLM extraction...")
        try:
            from src.tailor_engine import ResumeTailor
            tailor = ResumeTailor()
            # Try to extract better description using LLM
            improved_desc = tailor._create_tailoring_prompt(
                "", 
                {'description': job_data['description'], 'title': job_data['title'], 'company': job_data['company']}
            )
        except:
            pass
    
    status = "✅" if len(job_data['description']) > 100 else "⚠️"
    print(f"   {status} Title: {job_data['title']}")
    print(f"   {status} Company: {job_data['company']}")
    print(f"   {status} Description: {len(job_data['description'])} characters")
    
    if job_data.get('error'):
        print(f"   ⚠️  Warning: {job_data['error']}")
    
    return job_data

def scrape_jobs(urls, output_file=None):
    """Scrape multiple job URLs and save as JSON"""
    
    print(f"📋 Processing {len(urls)} job URL(s)...")
    
    jobs_data = []
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] ", end="")
        try:
            job_data = scrape_single_job(url)
            jobs_data.append(job_data)
            if len(job_data['description']) > 100:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {str(e)}")
            jobs_data.append({
                'url': url,
                'title': 'Error',
                'company': 'Unknown',
                'description': f'Failed to scrape: {str(e)}',
                'error': str(e)
            })
            failed += 1
    
    # Prepare output
    output_data = {
        'scraping_status': {
            'total_urls': len(urls),
            'successful': successful,
            'failed': failed,
            'short_descriptions': sum(1 for j in jobs_data if len(j['description']) < 500)
        },
        'jobs': jobs_data
    }
    
    # Determine output filename
    if not output_file:
        output_file = "jobs_scraped.json"
    
    # Save JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "="*60)
    print(f"✅ Results saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total jobs: {len(urls)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Short descriptions: {output_data['scraping_status']['short_descriptions']}")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scrape_jobs.py <url1> [url2] [url3] ... [output.json]")
        print("  python3 scrape_jobs.py --file urls.txt [output.json]")
        print("\nExamples:")
        print('  python3 scrape_jobs.py "https://boards.greenhouse.io/company/jobs/123"')
        print('  python3 scrape_jobs.py url1 url2 url3 my_jobs.json')
        print('  python3 scrape_jobs.py --file job_urls.txt')
        sys.exit(1)
    
    # Check for --file flag
    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a file with URLs")
            sys.exit(1)
        
        urls_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if not os.path.exists(urls_file):
            print(f"❌ Error: File not found: {urls_file}")
            sys.exit(1)
        
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print(f"❌ Error: No URLs found in {urls_file}")
            sys.exit(1)
        
        scrape_jobs(urls, output_file)
    
    else:
        # URLs provided as arguments
        # Last argument might be output file (ends with .json)
        args = sys.argv[1:]
        
        if args[-1].endswith('.json') and len(args) > 1:
            urls = args[:-1]
            output_file = args[-1]
        else:
            urls = args
            output_file = None
        
        scrape_jobs(urls, output_file)