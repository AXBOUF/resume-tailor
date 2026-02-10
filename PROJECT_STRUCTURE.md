# AI Resume Tailor - Project Structure

## Overview
This project has been reorganized into a clean, modular structure separating concerns between backend, frontend, data, and documentation.

## Directory Structure

```
resume-tailor/
├── README.md                 # Main project documentation
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Docker image definition
│
├── backend/                 # Backend code
│   ├── main.py             # FastAPI web server
│   ├── app.py              # Streamlit UI (alternative)
│   ├── src/                # Core modules
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration settings
│   │   ├── resume_parser.py
│   │   ├── job_scraper.py
│   │   ├── tailor_engine.py
│   │   ├── latex_generator.py
│   │   └── output_generator.py
│   └── cli/                # Command-line tools
│       ├── parse_resume.py
│       ├── scrape_jobs.py
│       ├── scrape_jobs_v2.py
│       ├── tailor_resume.py
│       ├── tailor_resume_latex.py
│       └── diagnose.py
│
├── frontend/               # Web frontend
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
│
├── data/                   # Data storage
│   ├── input/             # Input files (resumes)
│   └── output/            # Generated files
│
├── scripts/               # Utility scripts
│   ├── docker-run.sh
│   └── setup_env.sh
│
├── docs/                  # Documentation
│   ├── MODULAR_README.md
│   └── tmrrow.md
│
└── tests/                 # Test files (empty, for future)
```

## Usage

### Web Interface (FastAPI)
```bash
cd backend
python main.py
# Open http://localhost:8000
```

### Command Line Tools
```bash
cd backend/cli
python parse_resume.py ../../data/input/your_resume.pdf
python scrape_jobs_v2.py "https://jobs.lever.co/company/job"
python tailor_resume_latex.py ../../data/output/resume_parsed.json ../../data/output/jobs_scraped.json ../../data/output
```

### Streamlit UI (Alternative)
```bash
cd backend
streamlit run app.py
```

### Docker
```bash
./scripts/docker-run.sh
```

## Environment Setup
1. Copy `.env.example` to `.env`
2. Add your Groq API key to `.env`
3. Install dependencies: `pip install -r requirements.txt`

## Key Features
- AI-powered resume tailoring
- Job scraping from 50+ platforms
- ATS-optimized LaTeX output
- Web UI with smooth animations
- CLI tools for automation
- Docker support
