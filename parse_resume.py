#!/usr/bin/env python3
"""
Tool 1: Resume Parser
Input: PDF or DOCX resume file
Output: JSON file with structured resume data

Usage: python3 parse_resume.py <resume_file.pdf|docx> [output.json]

NOTE: If using virtual environment (venv), activate it first:
  source venv/bin/activate
  python3 parse_resume.py ...

Or use venv Python directly:
  ./venv/bin/python3 parse_resume.py ...
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.resume_parser import ResumeParser

def parse_resume(input_file, output_file=None):
    """Parse resume and save as JSON"""
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    # Detect file type
    file_extension = input_file.split('.')[-1].lower()
    if file_extension not in ['pdf', 'docx', 'doc']:
        print(f"❌ Error: Unsupported file type: {file_extension}")
        print("   Supported: pdf, docx, doc")
        sys.exit(1)
    
    # Parse
    print(f"📄 Parsing resume: {input_file}")
    parser = ResumeParser()
    
    try:
        resume_data = parser.parse_file(input_file, file_extension)
        
        # Add metadata
        output_data = {
            'source_file': input_file,
            'file_type': file_extension,
            'parsing_status': 'success',
            'contact_info': resume_data.get('contact_info', {}),
            'sections': resume_data.get('sections', {}),
            'full_text': resume_data.get('raw_text', ''),
            'line_count': len(resume_data.get('lines', []))
        }
        
        # Determine output filename
        if not output_file:
            base_name = '.'.join(input_file.split('.')[:-1])
            output_file = f"{base_name}_parsed.json"
        
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Success! Parsed resume saved to: {output_file}")
        print(f"\n📊 Summary:")
        print(f"   Lines parsed: {output_data['line_count']}")
        print(f"   Contact info: {len(output_data['contact_info'])} fields")
        print(f"   Sections found: {list(output_data['sections'].keys())}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error parsing resume: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_resume.py <resume_file.pdf|docx> [output.json]")
        print("\nExample:")
        print("  python3 parse_resume.py my_resume.pdf")
        print("  python3 parse_resume.py my_resume.docx resume_data.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    parse_resume(input_file, output_file)