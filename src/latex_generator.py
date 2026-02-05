# Resume Tailor - LaTeX Generator
# Generates Jake's Resume template formatted LaTeX files

import os
import re
from datetime import datetime
from typing import Dict, List, Any

class JakeResumeLaTeXGenerator:
    """Generate professional resumes using Jake's Resume LaTeX template"""
    
    def __init__(self):
        self.template = self._get_template()
    
    def _get_template(self) -> str:
        """Return the Jake's Resume LaTeX template preamble"""
        return r'''%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
% Modified by: AI Resume Tailor
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

%----------FONT OPTIONS----------
% sans-serif
% \usepackage[sfdefault]{FiraSans}
% \usepackage[sfdefault]{roboto}
% \usepackage[sfdefault]{noto-sans}
% \usepackage[default]{sourcesanspro}

% serif
% \usepackage{CormorantGaramond}
% \usepackage{charter}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING----------
'''

    def generate_heading(self, contact_info: Dict[str, str]) -> str:
        """Generate the heading section"""
        name = contact_info.get('name', 'Your Name')
        phone = contact_info.get('phone', '')
        email = contact_info.get('email', '')
        linkedin = contact_info.get('linkedin', '')
        github = contact_info.get('portfolio', '')
        
        # Clean up URLs
        if linkedin and not linkedin.startswith('http'):
            linkedin = f'https://{linkedin}'
        if github and not github.startswith('http'):
            github = f'https://{github}'
        
        heading = f"\\begin{{center}}\n"
        heading += f"    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}\n"
        heading += f"    \\small "
        
        contact_parts = []
        if phone:
            contact_parts.append(phone)
        if email:
            contact_parts.append(f"\\href{{mailto:{email}}}{{\\underline{{{email}}}}}")
        if linkedin:
            linkedin_display = linkedin.replace('https://', '').replace('http://', '')
            contact_parts.append(f"\\href{{{linkedin}}}{{\\underline{{{linkedin_display}}}}}")
        if github:
            github_display = github.replace('https://', '').replace('http://', '')
            contact_parts.append(f"\\href{{{github}}}{{\\underline{{{github_display}}}}}")
        
        heading += " $|$ ".join(contact_parts)
        heading += "\n\\end{center}\n\n"
        
        return heading
    
    def generate_education(self, education_items: List[Dict[str, str]]) -> str:
        """Generate education section"""
        if not education_items:
            return ""
        
        latex = "%-----------EDUCATION-----------\n"
        latex += "\\section{Education}\n"
        latex += "  \\resumeSubHeadingListStart\n"
        
        for edu in education_items:
            school = edu.get('school', edu.get('institution', 'School Name'))
            location = edu.get('location', '')
            degree = edu.get('degree', 'Degree')
            dates = edu.get('dates', edu.get('graduation_date', ''))
            
            latex += f"    \\resumeSubheading\n"
            latex += f"      {{{school}}}{{{location}}}\n"
            latex += f"      {{{degree}}}{{{dates}}}\n"
        
        latex += "  \\resumeSubHeadingListEnd\n\n"
        return latex
    
    def generate_experience(self, experience_items: List[Dict[str, Any]]) -> str:
        """Generate experience section with bullet points"""
        if not experience_items:
            return ""
        
        latex = "%-----------EXPERIENCE-----------\n"
        latex += "\\section{Experience}\n"
        latex += "  \\resumeSubHeadingListStart\n"
        
        for exp in experience_items:
            company = exp.get('company', 'Company Name')
            location = exp.get('location', '')
            title = exp.get('title', 'Job Title')
            dates = exp.get('dates', exp.get('duration', ''))
            
            latex += f"    \\resumeSubheading\n"
            latex += f"      {{{title}}}{{{dates}}}\n"
            latex += f"      {{{company}}}{{{location}}}\n"
            latex += "      \\resumeItemListStart\n"
            
            # Handle bullets
            bullets = exp.get('bullets', exp.get('description', []))
            if isinstance(bullets, str):
                # Split long text into bullets
                bullets = self._text_to_bullets(bullets)
            
            for bullet in bullets:
                if bullet.strip():
                    # Escape special LaTeX characters
                    bullet = self._escape_latex(bullet.strip())
                    latex += f"        \\resumeItem{{{bullet}}}\n"
            
            latex += "      \\resumeItemListEnd\n"
        
        latex += "  \\resumeSubHeadingListEnd\n\n"
        return latex
    
    def generate_projects(self, project_items: List[Dict[str, Any]]) -> str:
        """Generate projects section"""
        if not project_items:
            return ""
        
        latex = "%-----------PROJECTS-----------\n"
        latex += "\\section{Projects}\n"
        latex += "    \\resumeSubHeadingListStart\n"
        
        for project in project_items:
            name = project.get('name', 'Project Name')
            tech_stack = project.get('tech_stack', project.get('technologies', ''))
            
            latex += f"      \\resumeProjectHeading\n"
            latex += f"          {{\\textbf{{{name}}} $|$ \\emph{{{tech_stack}}}}}{{}}\n"
            latex += "          \\resumeItemListStart\n"
            
            bullets = project.get('bullets', project.get('description', []))
            if isinstance(bullets, str):
                bullets = self._text_to_bullets(bullets)
            
            for bullet in bullets:
                if bullet.strip():
                    bullet = self._escape_latex(bullet.strip())
                    latex += f"            \\resumeItem{{{bullet}}}\n"
            
            latex += "          \\resumeItemListEnd\n"
        
        latex += "    \\resumeSubHeadingListEnd\n\n"
        return latex
    
    def generate_skills(self, skills_data: Dict[str, str]) -> str:
        """Generate technical skills section"""
        latex = "%-----------PROGRAMMING SKILLS-----------\n"
        latex += "\\section{Technical Skills}\n"
        latex += " \\begin{itemize}[leftmargin=0.15in, label={}]\n"
        latex += "    \\small{\\item{\n"
        
        skill_lines = []
        if skills_data.get('languages'):
            skill_lines.append(f"     \\textbf{{Languages}}{{ : {skills_data['languages']}}} \\\\")
        if skills_data.get('frameworks'):
            skill_lines.append(f"     \\textbf{{Frameworks}}{{ : {skills_data['frameworks']}}} \\\\")
        if skills_data.get('developer_tools'):
            skill_lines.append(f"     \\textbf{{Developer Tools}}{{ : {skills_data['developer_tools']}}} \\\\")
        if skills_data.get('libraries'):
            skill_lines.append(f"     \\textbf{{Libraries}}{{ : {skills_data['libraries']}}} \\\\")
        
        latex += "\n".join(skill_lines)
        latex += "\n    }}\n"
        latex += " \\end{itemize}\n\n"
        
        return latex
    
    def generate_full_resume(self, data: Dict[str, Any]) -> str:
        """Generate complete LaTeX resume"""
        latex = self.template
        
        # Add heading
        latex += self.generate_heading(data.get('heading', {}))
        
        # Add sections
        if data.get('education'):
            latex += self.generate_education(data['education'])
        
        if data.get('experience'):
            latex += self.generate_experience(data['experience'])
        
        if data.get('projects'):
            latex += self.generate_projects(data['projects'])
        
        if data.get('skills'):
            latex += self.generate_skills(data['skills'])
        
        # Close document
        latex += "\n%-------------------------------------------\n"
        latex += "\\end{document}\n"
        
        return latex
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        # Order matters - escape backslash first
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        return text
    
    def _text_to_bullets(self, text: str) -> List[str]:
        """Convert paragraph text to bullet points"""
        # Split on periods, but keep the period
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullets = []
        
        current_bullet = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If sentence is too short, combine with next
            if len(sentence) < 30 and current_bullet:
                current_bullet += " " + sentence
            else:
                if current_bullet:
                    bullets.append(current_bullet)
                current_bullet = sentence
        
        if current_bullet:
            bullets.append(current_bullet)
        
        # Ensure we don't have too many bullets
        if len(bullets) > 5:
            # Combine shortest bullets
            while len(bullets) > 5:
                # Find shortest bullet
                shortest_idx = min(range(len(bullets)), key=lambda i: len(bullets[i]))
                if shortest_idx < len(bullets) - 1:
                    bullets[shortest_idx] = bullets[shortest_idx] + " " + bullets.pop(shortest_idx + 1)
                else:
                    bullets[shortest_idx - 1] = bullets[shortest_idx - 1] + " " + bullets.pop(shortest_idx)
        
        return bullets