#!/usr/bin/env python3
"""
FastAPI Web Server for AI Resume Tailor
Interactive website with smooth animations
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


def compile_latex_to_pdf(latex_file: str, pdf_file: str) -> bool:
    """Compile LaTeX file to PDF using pdflatex"""
    try:
        # Run pdflatex twice for proper references
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', 
                 os.path.dirname(pdf_file), latex_file],
                capture_output=True,
                text=True,
                timeout=60
            )
        return os.path.exists(pdf_file)
    except Exception as e:
        print(f"Error compiling LaTeX: {e}")
        return False

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.resume_parser import ResumeParser
from src.job_scraper import JobScraper
from src.tailor_engine import ResumeTailor
from src.latex_generator import JakeResumeLaTeXGenerator
from src.config import GROQ_API_KEY

app = FastAPI(title="AI Resume Tailor", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Create necessary directories
os.makedirs("../data/output", exist_ok=True)

# Store job status
job_status = {}

executor = ThreadPoolExecutor(max_workers=3)


class JobRequest(BaseModel):
    urls: List[str]


class TailorRequest(BaseModel):
    job_ids: List[str]


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("../frontend/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Parse uploaded resume file"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume
        parser = ResumeParser()
        file_ext = Path(file.filename).suffix.lower().replace('.', '')
        parsed_data = parser.parse_file(temp_path, file_ext)
        
        # Save to output directory
        output_path = f"../data/output/resume_parsed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w') as f:
            json.dump(parsed_data, f, indent=2)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return {
            "success": True,
            "data": parsed_data,
            "output_file": output_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape-jobs")
async def scrape_jobs(request: JobRequest, background_tasks: BackgroundTasks):
    """Scrape job descriptions from URLs"""
    job_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
    job_status[job_id] = {"status": "pending", "progress": 0, "jobs": [], "errors": []}
    
    # Run scraping in background
    background_tasks.add_task(scrape_jobs_task, job_id, request.urls)
    
    return {"job_id": job_id, "message": "Scraping started"}


def scrape_jobs_task(job_id: str, urls: List[str]):
    """Background task for job scraping"""
    scraper = JobScraper()
    jobs = []
    errors = []
    
    total = len(urls)
    for i, url in enumerate(urls):
        try:
            job_status[job_id]["status"] = "scraping"
            job_status[job_id]["progress"] = int((i / total) * 100)
            
            job_data = scraper.scrape_job(url)
            if job_data:
                job_data["url"] = url
                jobs.append(job_data)
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
    
    # Save results
    output_file = f"../data/output/jobs_scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(jobs, f, indent=2)
    
    job_status[job_id]["status"] = "completed"
    job_status[job_id]["progress"] = 100
    job_status[job_id]["jobs"] = jobs
    job_status[job_id]["errors"] = errors
    job_status[job_id]["output_file"] = output_file


@app.get("/api/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of background job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status[job_id]


@app.post("/api/tailor-resume")
async def tailor_resume(
    resume_file: str = Form(...),
    jobs_file: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    """Generate tailored resumes"""
    job_id = f"tailor_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(resume_file)}"
    job_status[job_id] = {"status": "pending", "progress": 0, "files": [], "errors": []}
    
    # Run tailoring in background
    if background_tasks:
        background_tasks.add_task(tailor_resume_task, job_id, resume_file, jobs_file)
    
    return {"job_id": job_id, "message": "Tailoring started"}


def tailor_resume_task(job_id: str, resume_file: str, jobs_file: str):
    """Background task for resume tailoring"""
    try:
        job_status[job_id]["status"] = "tailoring"
        
        # Load data
        with open(resume_file, 'r') as f:
            resume_data = json.load(f)
        
        with open(jobs_file, 'r') as f:
            jobs_data = json.load(f)
        
        tailor = ResumeTailor()
        latex_gen = JakeResumeLaTeXGenerator()
        
        generated_files = []
        total = len(jobs_data)
        
        for i, job in enumerate(jobs_data):
            job_status[job_id]["progress"] = int((i / total) * 100)
            
            try:
                # Tailor resume
                tailored_text = tailor.tailor_resume(resume_data, job)
                
                # Save tailored text
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                company = job.get('company', 'Unknown').replace(' ', '_')
                text_file = f"../data/output/{company}_{timestamp}.txt"
                
                with open(text_file, 'w') as f:
                    f.write(f"Tailored Resume for: {job.get('title', 'Unknown')}\n")
                    f.write(f"Company: {job.get('company', 'Unknown')}\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(tailored_text)
                
                generated_files.append({
                    "company": job.get('company', 'Unknown'),
                    "title": job.get('title', 'Unknown'),
                    "text": text_file,
                    "job_url": job.get('url', '')
                })
            except Exception as e:
                job_status[job_id]["errors"].append({
                    "job": job.get('title', 'Unknown'),
                    "error": str(e)
                })
        
        job_status[job_id]["status"] = "completed"
        job_status[job_id]["progress"] = 100
        job_status[job_id]["files"] = generated_files
        
    except Exception as e:
        job_status[job_id]["status"] = "error"
        job_status[job_id]["errors"].append(str(e))


@app.get("/api/download/{file_path:path}")
async def download_file(file_path: str):
    """Download generated file"""
    full_path = os.path.join("../data/output", file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        full_path,
        filename=os.path.basename(full_path),
        media_type='application/octet-stream'
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "groq_api_configured": bool(GROQ_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
