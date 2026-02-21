from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from fpdf import FPDF
import re
import os
from typing import Dict, Any
from src.config import OUTPUT_DIR

class ResumeGenerator:
    """Generate tailored resumes in DOCX and PDF formats"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_docx(self, resume_text: str, job_data: Dict[str, str], filename: str) -> str:
        """Generate DOCX file from tailored resume text"""
        doc = Document()
        
        # Set up document styles
        self._setup_document_styles(doc)
        
        # Parse and format the resume
        sections = self._parse_resume_sections(resume_text)
        
        # Add contact information (centered, large)
        if sections.get('contact'):
            contact_para = doc.add_paragraph()
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = contact_para.add_run(sections['contact'])
            run.font.size = Pt(12)
            run.font.bold = True
            doc.add_paragraph()  # Spacing
        
        # Add name/title at top if present
        if sections.get('name'):
            name_para = doc.add_paragraph()
            name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = name_para.add_run(sections['name'])
            run.font.size = Pt(16)
            run.font.bold = True
            doc.add_paragraph()
        
        # Add each section
        for section_name, content in sections.items():
            if section_name in ['contact', 'name']:
                continue
                
            if content:
                # Section header
                header = doc.add_paragraph()
                header_run = header.add_run(section_name.upper())
                header_run.font.size = Pt(12)
                header_run.font.bold = True
                
                # Add underline
                header_format = header.paragraph_format
                header_format.space_after = Pt(6)
                
                # Add content
                for line in content:
                    if line.strip():
                        para = doc.add_paragraph(line.strip(), style='List Bullet' if line.strip().startswith('•') else 'Normal')
                        para.paragraph_format.space_after = Pt(3)
                
                doc.add_paragraph()  # Spacing between sections
        
        # If no sections parsed, add raw text
        if len(sections) <= 2:  # Only contact and/or name
            raw_para = doc.add_paragraph(resume_text)
        
        # Save document
        output_path = os.path.join(self.output_dir, filename)
        doc.save(output_path)
        return output_path
    
    def generate_pdf(self, resume_text: str, job_data: Dict[str, str], filename: str) -> str:
        """Generate PDF file from tailored resume text"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Parse sections
        sections = self._parse_resume_sections(resume_text)
        
        # Set fonts
        pdf.set_font("Arial", 'B', 16)
        
        # Add name
        if sections.get('name'):
            pdf.cell(0, 10, sections['name'], ln=True, align='C')
            pdf.ln(5)
        
        # Add contact info
        if sections.get('contact'):
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, sections['contact'], ln=True, align='C')
            pdf.ln(10)
        
        # Add sections
        for section_name, content in sections.items():
            if section_name in ['contact', 'name']:
                continue
                
            if content:
                # Section header
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, section_name.upper(), ln=True)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
                
                # Content
                pdf.set_font("Arial", '', 10)
                for line in content:
                    if line.strip():
                        # Handle bullet points
                        if line.strip().startswith('•'):
                            pdf.cell(5)  # Indent
                            pdf.multi_cell(0, 5, line.strip())
                        else:
                            pdf.multi_cell(0, 5, line.strip())
                
                pdf.ln(5)
        
        # If no sections parsed, add raw text
        if len(sections) <= 2:
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, resume_text)
        
        # Save PDF
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        return output_path
    
    def generate_both_formats(self, resume_text: str, job_data: Dict[str, str], base_filename: str) -> Dict[str, str]:
        """Generate both DOCX and PDF versions"""
        # Clean filename
        company = job_data.get('company', 'Unknown').replace(' ', '_')
        title = job_data.get('title', 'Position').replace(' ', '_')
        safe_base = f"{base_filename}_{company}_{title}".replace('/', '_').replace('\\', '_')
        
        docx_filename = f"{safe_base}.docx"
        pdf_filename = f"{safe_base}.pdf"
        
        docx_path = self.generate_docx(resume_text, job_data, docx_filename)
        pdf_path = self.generate_pdf(resume_text, job_data, pdf_filename)
        
        return {
            'docx': docx_path,
            'pdf': pdf_path,
            'docx_name': docx_filename,
            'pdf_name': pdf_filename
        }
    
    def _setup_document_styles(self, doc: Document):
        """Set up document styles for DOCX"""
        # Modify Normal style
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        
        # Set up List Bullet style
        try:
            bullet_style = doc.styles['List Bullet']
            bullet_style.font.name = 'Arial'
            bullet_style.font.size = Pt(11)
        except:
            pass
    
    def _parse_resume_sections(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text into sections"""
        sections = {
            'name': '',
            'contact': '',
        }
        
        lines = resume_text.split('\n')
        current_section = None
        current_content = []
        
        # Common section headers
        section_keywords = {
            'summary': ['summary', 'professional summary', 'objective', 'profile'],
            'experience': ['experience', 'work experience', 'professional experience', 'employment', 'work history'],
            'education': ['education', 'academic', 'degrees', 'university', 'college'],
            'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies', 'tools'],
            'certifications': ['certifications', 'certificates', 'licenses', 'accreditations'],
            'projects': ['projects', 'personal projects', 'side projects', 'portfolio'],
            'awards': ['awards', 'honors', 'achievements', 'recognition'],
            'publications': ['publications', 'papers', 'research']
        }
        
        # Extract name and contact from first few lines
        for i, line in enumerate(lines[:10]):
            if not sections['name'] and len(line.strip().split()) <= 4:
                # Assume first short line is name
                if not any(x in line.lower() for x in ['email', 'phone', 'linkedin', '@', 'http']):
                    sections['name'] = line.strip()
                    continue
            
            # Look for contact info patterns
            if any(x in line.lower() for x in ['email', 'phone', 'linkedin', '@', 'http', 'github']):
                if sections['contact']:
                    sections['contact'] += ' | ' + line.strip()
                else:
                    sections['contact'] = line.strip()
        
        # Parse sections
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if this is a section header
            is_header = False
            line_lower = line_stripped.lower()
            
            # Remove common punctuation from header detection
            clean_line = re.sub(r'[:\-\*=_#]+$', '', line_lower).strip()
            
            for section_name, keywords in section_keywords.items():
                if any(keyword in clean_line for keyword in keywords):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = current_content
                    
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line_stripped)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = current_content
        
        return sections