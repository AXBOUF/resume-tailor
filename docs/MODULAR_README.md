# Resume Tailor - Modular Tools

## Overview

This application is now split into **3 independent tools**, each producing JSON output that can be chained together.

## The 3 Tools

### Tool 1: parse_resume.py
**Purpose**: Extract structured data from PDF/DOCX resumes  
**Input**: Resume file (PDF or DOCX)  
**Output**: JSON file with parsed resume data

```bash
python3 parse_resume.py my_resume.pdf
# Creates: my_resume_parsed.json

python3 parse_resume.py my_resume.docx output.json
# Creates: output.json
```

**Output JSON structure:**
```json
{
  "source_file": "my_resume.pdf",
  "file_type": "pdf",
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    ...
  },
  "sections": {
    "experience": [...],
    "education": [...],
    "skills": [...]
  },
  "full_text": "complete resume text..."
}
```

---

### Tool 2: scrape_jobs.py
**Purpose**: Scrape job descriptions from URLs  
**Input**: Job posting URLs  
**Output**: JSON file with job descriptions

```bash
# Single URL
python3 scrape_jobs.py "https://boards.greenhouse.io/company/jobs/123"

# Multiple URLs
python3 scrape_jobs.py url1 url2 url3

# Save to specific file
python3 scrape_jobs.py url1 url2 my_jobs.json

# URLs from file (one per line)
echo "url1" > urls.txt
echo "url2" >> urls.txt
python3 scrape_jobs.py --file urls.txt
```

**Output JSON structure:**
```json
{
  "scraping_status": {
    "total_urls": 3,
    "successful": 2,
    "failed": 1
  },
  "jobs": [
    {
      "url": "...",
      "title": "Software Engineer",
      "company": "TechCorp",
      "description": "full job description..."
    }
  ]
}
```

---

### Tool 2 v2: scrape_jobs_v2.py ⭐ **RECOMMENDED**
**Purpose**: Scrape + **CLEAN** job descriptions with noise removal
**Input**: Job posting URLs  
**Output**: Clean JSON with sections extracted and quality scoring

**Why use v2?** Removes UI noise (buttons, forms, ads) and extracts key sections:
- Role Overview
- Responsibilities  
- Requirements
- Benefits

```bash
# Standard scrape with cleaning
python3 scrape_jobs_v2.py "https://au.jora.com/job/..."

# Multiple URLs
python3 scrape_jobs_v2.py url1 url2 url3

# From file
python3 scrape_jobs_v2.py --file urls.txt

# Disable cleaning (raw like v1)
python3 scrape_jobs_v2.py --no-clean "https://..."

# Clean existing v1 JSON file
python3 scrape_jobs_v2.py --clean-only old_jobs.json
```

**Output JSON structure (much cleaner!):**
```json
{
  "version": "2.0",
  "statistics": {
    "total": 1,
    "successful": 1,
    "by_quality": {"excellent": 1, "good": 0, "fair": 0, "poor": 0}
  },
  "jobs": [
    {
      "url": "...",
      "title": "Software Engineer",
      "company": "TechCorp",
      "description": "clean job description...",
      "cleaning_metadata": {
        "original_length": 3628,
        "cleaned_length": 2785,
        "reduction_percent": 23.2,
        "quality_score": "excellent"
      },
      "sections": {
        "role_overview": "...",
        "responsibilities": "...",
        "requirements": "...",
        "benefits": "..."
      }
    }
  ]
}
```

**v1 vs v2 Comparison:**
| Feature | v1 | v2 |
|---------|----|----|
| Noise removal | ❌ No | ✅ Yes (20-40%) |
| Section extraction | ❌ No | ✅ Yes |
| Quality scoring | ❌ No | ✅ Yes |
| When to use | Greenhouse, Lever | Jora, Indeed, messy sites |

---

### Tool 3: tailor_resume_latex.py ⭐ **RECOMMENDED**
**Purpose**: Generate professional PDF resumes using Jake's Resume LaTeX template  
**Input**: Resume JSON + Jobs JSON  
**Output**: `.tex` files + compiled PDFs (Jake's Resume format)

**Why use LaTeX version?**
- ✅ Industry-standard Jake's Resume format (ATS-optimized)
- ✅ Professional typography and layout
- ✅ Converts experience to impactful bullet points
- ✅ Auto-categorizes skills (Languages/Frameworks/Tools/Libraries)
- ✅ Professional filenames: `FirstName_LastName_Role_Company.pdf`
- ✅ Ready to submit or upload to Overleaf for tweaks

```bash
# Generate LaTeX and PDF
python3 tailor_resume_latex.py resume_parsed.json jobs_scraped_v2.json

# Custom output directory
python3 tailor_resume_latex.py resume.json jobs.json ./my_resumes
```

**Output:**
- `Mun_Albaraili_Data_Engineer_Talenza.tex` (LaTeX source)
- `Mun_Albaraili_Data_Engineer_Talenza.pdf` (Compiled PDF)
- `tailoring_summary.json` (Metadata)

**PDF Compilation:**
- **Automatic**: If `pdflatex` is installed (texlive package)
- **Manual**: Upload `.tex` file to [Overleaf](https://www.overleaf.com) and recompile

---

### Tool 3 (Legacy): tailor_resume.py
**Purpose**: Create basic tailored resumes  
**Input**: Resume JSON + Jobs JSON  
**Output**: Simple DOCX and PDF files

**Note**: Use `tailor_resume_latex.py` instead for professional Jake's Resume formatting.

```bash
# Basic usage (legacy format)
python3 tailor_resume.py resume_parsed.json jobs_scraped.json
**Purpose**: Create tailored resumes using LLM  
**Input**: Resume JSON + Jobs JSON  
**Output**: DOCX and PDF files for each job

```bash
# Basic usage
python3 tailor_resume.py resume_parsed.json jobs_scraped.json

# Custom output directory
python3 tailor_resume.py resume.json jobs.json ./my_output
```

**Output:**
- `resume_01_CompanyName.docx`
- `resume_01_CompanyName.pdf`
- `resume_02_OtherCompany.docx`
- `resume_02_OtherCompany.pdf`
- `tailoring_summary.json` (summary of all outputs)

---

## Complete Workflow Example

### Step 1: Parse Your Resume
```bash
python3 parse_resume.py my_resume.pdf
# Output: my_resume_parsed.json
```

### Step 2: Scrape Job URLs
```bash
# Create a file with job URLs
cat > jobs.txt << EOF
https://boards.greenhouse.io/company1/jobs/123
https://jobs.lever.co/company2/456
https://example.com/careers/789
EOF

# Scrape them (use v2 for better cleaning!)
python3 scrape_jobs_v2.py --file jobs.txt
# Output: jobs_scraped_v2.json
```

### Step 3: Generate Tailored Resumes (LaTeX - Professional)
```bash
# Generate professional PDFs with Jake's Resume formatting
python3 tailor_resume_latex.py my_resume_parsed.json jobs_scraped_v2.json ./output

# Check results
ls -la ./output/
# Output: Mun_Albaraili_Data_Engineer_Talenza.pdf (Ready to apply!)
```

**No PDF compiler?** Upload the `.tex` file to [Overleaf](https://www.overleaf.com):
1. Go to overleaf.com
2. Click "New Project" → "Upload Project"
3. Upload the `.tex` file
4. Click "Recompile" → Download PDF

---

## Prerequisites

1. **Install dependencies**:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Set up API key**:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
echo "GROQ_API_KEY=your_key_here" > .env
```

Get free API key: https://console.groq.com/keys

3. **Optional: Install LaTeX for automatic PDF compilation**:
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# Arch Linux
sudo pacman -S texlive-most texlive-lang

# macOS
brew install --cask mactex
```

**OR** use [Overleaf](https://www.overleaf.com) (free, no installation needed) - just upload the generated `.tex` files.

---

## Benefits of This Modular Approach

✅ **Test each step independently** - Debug parsing, scraping, or tailoring separately  
✅ **Reuse outputs** - Parse resume once, scrape jobs later, tailor when ready  
✅ **Manual editing** - Edit JSON files between steps if needed  
✅ **Batch processing** - Process multiple jobs efficiently  
✅ **Version control** - Track changes to parsed data or job descriptions  
✅ **No UI needed** - Pure CLI tools, works in any terminal

---

## Alternative: Streamlit UI

If you prefer a web interface:
```bash
streamlit run app.py
```

The UI combines all 3 tools but the modular CLI tools give you more control.