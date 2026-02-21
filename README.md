# AI Resume Tailor 🤖📄

> **Open-source tool to automatically tailor your resume for multiple job applications using AI**

Transform one resume into multiple tailored versions - each optimized for specific job postings using the industry-standard Jake's Resume format.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange.svg)

---

## ✨ What It Does

**The Problem:** You apply to 20 jobs, you need 20 tailored resumes. Manual copy-pasting and reformatting takes hours.

**The Solution:** 
1. 📄 Upload your resume once
2. 🔗 Drop job posting URLs  
3. 🤖 AI automatically tailors your resume for each job
4. 📥 Download professional PDFs (Jake's Resume format) ready to submit

**Result:** Apply to more jobs with better tailored resumes in less time.

---

## 🚀 Quick Start (5 minutes)

### Step 1: Clone & Setup
```bash
git clone <your-repo-url>
cd resume-tailor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
python3 -m playwright install chromium
```

### Step 2: Get API Key
```bash
# Get free Groq API key (takes 30 seconds)
# https://console.groq.com/keys

echo "GROQ_API_KEY=your_key_here" > .env
```

### Step 3: Run It
```bash
# 1. Parse your resume
python3 parse_resume.py your_resume.pdf

# 2. Scrape job URLs
python3 scrape_jobs_v2.py "https://jobs.lever.co/company/job-id"

# 3. Generate tailored PDFs
python3 tailor_resume_latex.py resume_parsed.json jobs_scraped_v2.json

# Check output/
ls -la output/
# Mun_Albaraili_Data_Engineer_Talenza.pdf ✅
```

---

## 📋 Full Workflow Example

```bash
# Navigate to project
cd resume-tailor
source venv/bin/activate

# Step 1: Parse resume (one-time)
python3 parse_resume.py My_Resume.pdf
# Output: My_Resume_parsed.json

# Step 2: Scrape multiple job URLs
cat > jobs.txt << EOF
https://jobs.lever.co/company1/job-123
https://boards.greenhouse.io/company2/jobs/456
https://au.jora.com/job/Data-Scientist-...
EOF

python3 scrape_jobs_v2.py --file jobs.txt
# Output: jobs_scraped_v2.json

# Step 3: Generate all tailored resumes
python3 tailor_resume_latex.py \
  My_Resume_parsed.json \
  jobs_scraped_v2.json \
  ./output

# Results:
# output/
# ├── Mun_Albaraili_Data_Engineer_Company1.pdf
# ├── Mun_Albaraili_Data_Engineer_Company2.pdf
# ├── Mun_Albaraili_Data_Scientist_Company3.pdf
# └── tailoring_summary.json
```

---

## 🛠️ Available Tools

| Tool | Purpose | Output |
|------|---------|--------|
| `parse_resume.py` | Extract text from PDF/DOCX | JSON with structured data |
| `scrape_jobs_v2.py` | Scrape job descriptions from URLs | Clean JSON with sections |
| `tailor_resume_latex.py` | Generate Jake's Resume PDFs | `.tex` + `.pdf` files |

**Legacy tools also available:**
- `scrape_jobs.py` - Original scraper (no cleaning)
- `tailor_resume.py` - Basic DOCX generator

---

## 📁 Project Structure

```
resume-tailor/
├── src/
│   ├── resume_parser.py        # PDF/DOCX parsing
│   ├── job_scraper.py          # Web scraping
│   ├── tailor_engine.py        # Groq LLM integration
│   ├── latex_generator.py      # Jake's Resume LaTeX
│   └── config.py               # Configuration
├── parse_resume.py             # Tool 1: Resume parser
├── scrape_jobs_v2.py           # Tool 2: Job scraper (v2)
├── tailor_resume_latex.py      # Tool 3: LaTeX generator
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
└── MODULAR_README.md          # Detailed docs
```

---

## 💡 Key Features

✅ **Jake's Resume Format** - Industry-standard LaTeX template (ATS-optimized)  
✅ **Smart Cleaning** - Removes website UI noise from job descriptions (v2)  
✅ **AI Tailoring** - Uses Groq LLM to match your experience to job requirements  
✅ **Batch Processing** - Process multiple jobs at once  
✅ **Professional Output** - PDFs ready to submit  
✅ **Privacy-First** - No data leaves your machine except Groq API calls  
✅ **Open Source** - Free to use, modify, and share  

---

## 🎯 Output Format

Each generated resume follows the **Jake's Resume** format:

```
┌─────────────────────────────────────┐
│      Your Name                      │
│  Phone | Email | LinkedIn | GitHub  │
├─────────────────────────────────────┤
│ EDUCATION                           │
│ University | Degree | Dates         │
├─────────────────────────────────────┤
│ EXPERIENCE                          │
│ Company | Role | Dates              │
│ • Tailored achievement bullets      │
│ • Highlighted relevant skills       │
│ • Quantified impacts                │
├─────────────────────────────────────┤
│ PROJECTS                            │
│ Project Name | Tech Stack           │
│ • Relevant project details          │
├─────────────────────────────────────┤
│ TECHNICAL SKILLS                    │
│ Languages | Frameworks | Tools      │
└─────────────────────────────────────┘
```

---

## ⚙️ Configuration

Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

**Free Tier Limits:**
- 20 requests/minute
- 1,000,000 tokens/minute
- No credit card required

---

## 🐛 Troubleshooting

**Issue:** `ModuleNotFoundError`
```bash
# Solution: Activate venv
source venv/bin/activate
```

**Issue:** Playwright browser not found
```bash
# Solution: Install browsers
python3 -m playwright install chromium
```

**Issue:** Job scraping fails
- Some sites (LinkedIn) block scrapers
- Try: Greenhouse, Lever, company career pages
- Use `scrape_jobs_v2.py` for better cleaning

**Issue:** No PDF generated
- Install LaTeX: `sudo pacman -S texlive-most` (Arch)
- Or use Overleaf: Upload `.tex` file to overleaf.com

---

## 🤝 Contributing

This is a personal project that evolved into an open-source tool. Contributions welcome!

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📜 License

MIT License - Feel free to use for personal or commercial projects.

---

## 🙏 Acknowledgments

- **Jake's Resume** - The LaTeX template that powers the professional output
- **Groq** - Fast LLM inference (free tier)
- **Playwright** - Reliable web scraping
- **Streamlit** - Web UI framework

---

## 🔮 Roadmap

- [ ] Web UI (Streamlit) for non-technical users
- [ ] More resume templates
- [ ] LinkedIn integration
- [ ] Cover letter generation
- [ ] SaaS version (maybe)

---

**Made with ❤️ by job seekers, for job seekers**

*Stop tailoring resumes manually. Let AI do the work.*