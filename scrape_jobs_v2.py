#!/usr/bin/env python3
"""
Tool 2 v2: Improved Job Scraper
Input: URLs of job postings (one or multiple)
Output: Clean JSON file with job descriptions

Improvements over v1:
- Better content extraction using multiple strategies
- AI-powered cleaning to remove UI noise
- Section identification (requirements, responsibilities, etc.)
- Improved error handling and logging
- Support for more job boards

Usage: 
  python3 scrape_jobs_v2.py <url1> [url2] [url3] ... [output.json]
  python3 scrape_jobs_v2.py --file urls.txt [output.json]
  python3 scrape_jobs_v2.py --clean-only jobs_scraped.json [output.json]
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.job_scraper import JobScraper


class JobContentCleaner:
    """Clean scraped job content to remove UI noise and extract meaningful text"""
    
    # Common UI patterns to remove
    UI_PATTERNS = [
        r'Search jobs?',
        r'Begin typing for results?',
        r'Apply on company site',
        r'Sign in to start saving',
        r'Email address',
        r'Password',
        r'Log in',
        r'Forgot your password',
        r'Don\'t have an account',
        r'Sign up',
        r'Register with',
        r'Facebook',
        r'Apple',
        r'Google',
        r'Be careful[\s\S]*?report this job',
        r'Email to yourself[\s\S]*?Send to another email',
        r'Related job searches[\s\S]*?jobs',
        r'Apply\s*$',
        r'Do you want to receive recommendations[\s\S]*?unsubscribe anytime',
        r'By creating an email alert[\s\S]*?Privacy Policy',
        r',\s*from\s*\n',
        r'\d+d?\s*ago\s*,?\s*',
        r'Permanent\s*,?\s*',
        r'\$[\d,]+\s*[-–]\s*\$?[\d,]+.*?(?:a year|per year|annually)',
        r'Full[\s-]?time',
        r'Part[\s-]?time',
        r'Contract',
        r'Hybrid',
        r'Remote',
        r'\d+\+?\s*years?\s*(?:of)?\s*experience',
    ]
    
    # Section headers to preserve and identify
    SECTION_HEADERS = [
        r'(?:About\s+(?:the\s+)?Role|Job Description|Position Overview)',
        r'(?:Key\s+)?Responsibilities?|What You[\'\']ll Do|Duties',
        r'Requirements?|Qualifications?|What You[\'\']ll Bring|Skills?\s*(?:&|and)\s*Experience',
        r'(?:What[\'\']s\s+)?(?:on\s+)?Offer|Benefits?|Perks?|Compensation',
        r'About\s+(?:the\s+)?Company|Who We Are',
    ]
    
    def __init__(self):
        self.ui_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) 
                           for pattern in self.UI_PATTERNS]
        self.section_headers = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in self.SECTION_HEADERS]
    
    def clean(self, text: str) -> Dict[str, any]:
        """Clean job description and extract sections"""
        original_length = len(text)
        
        # Step 1: Remove UI patterns
        cleaned = text
        removed_patterns = []
        for i, pattern in enumerate(self.ui_patterns):
            matches = pattern.findall(cleaned)
            if matches:
                removed_patterns.extend(matches[:3])  # Limit logging
            cleaned = pattern.sub('', cleaned)
        
        # Step 2: Clean up excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        # Step 3: Remove lines that are likely UI elements
        lines = cleaned.split('\n')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip very short lines that might be buttons/labels
            if len(line) < 3:
                continue
            # Skip common UI labels
            if line.lower() in ['search', 'apply', 'save', 'share', 'report', 'back', 'next', 'submit']:
                continue
            filtered_lines.append(line)
        
        cleaned = '\n'.join(filtered_lines)
        
        # Step 4: Extract sections
        sections = self._extract_sections(cleaned)
        
        # Step 5: Calculate metrics
        cleaned_length = len(cleaned)
        reduction = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
        
        return {
            'cleaned_text': cleaned.strip(),
            'original_length': original_length,
            'cleaned_length': cleaned_length,
            'reduction_percent': round(reduction, 1),
            'sections': sections,
            'has_key_sections': len(sections) > 0,
            'quality_score': self._calculate_quality(cleaned, sections)
        }
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract key sections from job description"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        section_map = {
            r'(?:About\s+(?:the\s+)?Role|Job Description|Position Overview)': 'role_overview',
            r'(?:Key\s+)?Responsibilities?|What You[\'\']ll Do|Duties': 'responsibilities',
            r'Requirements?|Qualifications?|What You[\'\']ll Bring|Skills?\s*(?:&|and)\s*Experience': 'requirements',
            r'(?:What[\'\']s\s+)?(?:on\s+)?Offer|Benefits?|Perks?|Compensation': 'benefits',
            r'About\s+(?:the\s+)?Company|Who We Are': 'company_info',
        }
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if line is a section header
            is_header = False
            for pattern, section_name in section_map.items():
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line_stripped)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _calculate_quality(self, text: str, sections: Dict) -> str:
        """Calculate a quality score for the cleaned text"""
        score = 0
        
        # Points for length
        if len(text) > 1000:
            score += 2
        elif len(text) > 500:
            score += 1
        
        # Points for sections
        score += len(sections)
        
        # Points for key sections
        if 'requirements' in sections or 'responsibilities' in sections:
            score += 2
        
        if score >= 5:
            return 'excellent'
        elif score >= 3:
            return 'good'
        elif score >= 1:
            return 'fair'
        else:
            return 'poor'


class ImprovedJobScraper:
    """Improved job scraper with cleaning capabilities"""
    
    def __init__(self, use_cleaning: bool = True):
        self.base_scraper = JobScraper()
        self.cleaner = JobContentCleaner() if use_cleaning else None
        self.use_cleaning = use_cleaning
    
    def scrape_job(self, url: str) -> Dict:
        """Scrape and optionally clean job data"""
        # Use base scraper to get raw data
        raw_data = self.base_scraper.scrape_job(url)
        
        if self.cleaner and raw_data.get('description'):
            # Clean the description
            cleaning_result = self.cleaner.clean(raw_data['description'])
            
            # Update with cleaned data
            raw_data['description'] = cleaning_result['cleaned_text']
            raw_data['cleaning_metadata'] = {
                'original_length': cleaning_result['original_length'],
                'cleaned_length': cleaning_result['cleaned_length'],
                'reduction_percent': cleaning_result['reduction_percent'],
                'quality_score': cleaning_result['quality_score'],
                'has_key_sections': cleaning_result['has_key_sections']
            }
            raw_data['sections'] = cleaning_result['sections']
        
        return raw_data


def scrape_jobs_v2(urls: List[str], output_file: str = None, use_cleaning: bool = True) -> str:
    """Scrape multiple jobs with improved cleaning"""
    
    print(f"📋 Processing {len(urls)} job URL(s)...")
    print(f"🧹 Cleaning enabled: {use_cleaning}")
    
    scraper = ImprovedJobScraper(use_cleaning=use_cleaning)
    jobs_data = []
    stats = {
        'total': len(urls),
        'successful': 0,
        'failed': 0,
        'by_quality': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
    }
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 🔍 Scraping: {url[:80]}...")
        
        try:
            job_data = scraper.scrape_job(url)
            jobs_data.append(job_data)
            
            # Update stats
            if job_data.get('cleaning_metadata'):
                quality = job_data['cleaning_metadata']['quality_score']
                stats['by_quality'][quality] = stats['by_quality'].get(quality, 0) + 1
                
                print(f"   ✅ {job_data['title'][:60]} @ {job_data['company'][:30]}")
                print(f"   📊 Quality: {quality.upper()}")
                print(f"   📝 Length: {job_data['cleaning_metadata']['cleaned_length']} chars")
                print(f"   🧹 Cleaned: {job_data['cleaning_metadata']['reduction_percent']}% noise removed")
                stats['successful'] += 1
            else:
                print(f"   ✅ {job_data['title'][:60]} @ {job_data['company'][:30]}")
                print(f"   📝 Length: {len(job_data['description'])} chars (no cleaning)")
                stats['successful'] += 1
                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            jobs_data.append({
                'url': url,
                'title': 'Error',
                'company': 'Unknown',
                'description': f'Failed to scrape: {str(e)}',
                'error': str(e)
            })
            stats['failed'] += 1
    
    # Prepare output
    output_data = {
        'version': '2.0',
        'scraping_config': {
            'cleaning_enabled': use_cleaning,
            'total_urls': len(urls)
        },
        'statistics': stats,
        'jobs': jobs_data
    }
    
    # Save
    if not output_file:
        output_file = "jobs_scraped_v2.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n" + "="*70)
    print(f"✅ Results saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total: {stats['total']} | Successful: {stats['successful']} | Failed: {stats['failed']}")
    if use_cleaning:
        print(f"\n🎯 Quality Distribution:")
        for quality, count in stats['by_quality'].items():
            if count > 0:
                print(f"      {quality.capitalize()}: {count}")
    
    return output_file


def clean_existing_json(input_file: str, output_file: str = None):
    """Clean an existing jobs JSON file"""
    print(f"🧹 Cleaning existing file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    cleaner = JobContentCleaner()
    
    cleaned_count = 0
    for job in jobs:
        if job.get('description') and not job.get('cleaning_metadata'):
            result = cleaner.clean(job['description'])
            job['description'] = result['cleaned_text']
            job['cleaning_metadata'] = {
                'original_length': result['original_length'],
                'cleaned_length': result['cleaned_length'],
                'reduction_percent': result['reduction_percent'],
                'quality_score': result['quality_score']
            }
            job['sections'] = result['sections']
            cleaned_count += 1
    
    data['version'] = '2.0 (cleaned)'
    data['cleaning_applied'] = True
    
    if not output_file:
        base = input_file.replace('.json', '')
        output_file = f"{base}_cleaned.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Cleaned {cleaned_count} jobs and saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("scrape_jobs_v2.py - Improved Job Scraper")
        print("\nUsage:")
        print("  python3 scrape_jobs_v2.py <url1> [url2] [url3] ... [output.json]")
        print("  python3 scrape_jobs_v2.py --file urls.txt [output.json]")
        print("  python3 scrape_jobs_v2.py --clean-only jobs_scraped.json [output.json]")
        print("  python3 scrape_jobs_v2.py --no-clean <url1> ...  # Disable cleaning")
        print("\nExamples:")
        print('  python3 scrape_jobs_v2.py "https://jobs.lever.co/company/job"')
        print('  python3 scrape_jobs_v2.py --file job_urls.txt my_jobs.json')
        print('  python3 scrape_jobs_v2.py --clean-only old_jobs.json')
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    use_cleaning = True
    
    if '--no-clean' in args:
        use_cleaning = False
        args.remove('--no-clean')
    
    # Handle --clean-only mode
    if args[0] == '--clean-only':
        if len(args) < 2:
            print("❌ Error: Please provide a JSON file to clean")
            sys.exit(1)
        input_file = args[1]
        output_file = args[2] if len(args) > 2 else None
        clean_existing_json(input_file, output_file)
        sys.exit(0)
    
    # Handle --file mode
    if args[0] == '--file':
        if len(args) < 2:
            print("❌ Error: Please provide a file with URLs")
            sys.exit(1)
        
        urls_file = args[1]
        output_file = args[2] if len(args) > 2 else None
        
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        # URLs provided directly
        # Last arg might be output file
        if args[-1].endswith('.json') and len(args) > 1:
            urls = args[:-1]
            output_file = args[-1]
        else:
            urls = args
            output_file = None
    
    scrape_jobs_v2(urls, output_file, use_cleaning)