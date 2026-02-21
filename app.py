import streamlit as st
import os
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.resume_parser import ResumeParser
from src.job_scraper import JobScraper
from src.tailor_engine import ResumeTailor
from src.output_generator import ResumeGenerator
from src.config import GROQ_API_KEY, OUTPUT_DIR

st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .job-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize session state variables"""
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'jobs' not in st.session_state:
        st.session_state.jobs = []
    if 'tailored_resumes' not in st.session_state:
        st.session_state.tailored_resumes = []
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = []
    
    # Ensure jobs is always a list
    if not isinstance(st.session_state.jobs, list):
        st.session_state.jobs = []

def check_api_key():
    """Check if Groq API key is configured"""
    if not GROQ_API_KEY or GROQ_API_KEY == 'your_groq_api_key_here':
        st.error("⚠️ Groq API key not configured!")
        st.info("Please create a `.env` file with your GROQ_API_KEY. Get your free key at: https://console.groq.com/keys")
        st.code("GROQ_API_KEY=your_actual_key_here", language="bash")
        return False
    return True

def step_1_upload_resume():
    """Step 1: Upload original resume"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### 📤 Step 1: Upload Your Resume")
    st.write("Upload your current resume in PDF or DOCX format. This will be used as the base for all tailored versions.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'doc'],
        help="Upload your resume in PDF or Word format"
    )
    
    if uploaded_file is not None:
        with st.spinner("Parsing your resume..."):
            try:
                # Save uploaded file temporarily
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Parse the resume
                parser = ResumeParser()
                resume_data = parser.parse_file(tmp_path, file_extension)
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                # Store in session
                st.session_state.resume_data = resume_data
                
                # Show preview
                st.success(f"✅ Resume parsed successfully! Found {len(resume_data.get('lines', []))} lines.")
                
                with st.expander("Preview parsed resume"):
                    st.json(resume_data.get('contact_info', {}))
                    for section, content in resume_data.get('sections', {}).items():
                        if content:
                            st.write(f"**{section.title()}:** {len(content)} lines")
                
                if st.button("Continue to Step 2 →", type="primary"):
                    st.session_state.current_step = 2
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error parsing resume: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_2_add_jobs():
    """Step 2: Add job URLs"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### 🔗 Step 2: Add Job Posting URLs")
    st.write("Enter the URLs of job postings you want to apply for. We'll automatically extract the job descriptions.")
    
    # Debug info
    if st.session_state.jobs:
        st.info(f"✅ Currently have {len(st.session_state.jobs)} job(s) in queue")
    
    # Input method selection
    input_method = st.radio(
        "How would you like to add jobs?",
        ["Enter URLs one by one", "Paste multiple URLs"],
        horizontal=True,
        key="input_method"
    )
    
    # Use a form to prevent premature reruns
    if input_method == "Enter URLs one by one":
        with st.form("single_job_form", clear_on_submit=True):
            job_url = st.text_input("Job posting URL", placeholder="https://...", key="single_url")
            submit = st.form_submit_button("➕ Add Job", use_container_width=True)
            
        if submit and job_url:
            with st.spinner("Scraping job description..."):
                try:
                    scraper = JobScraper()
                    job_data = scraper.scrape_job(job_url)
                    st.session_state.jobs.append(job_data)
                    st.success(f"✅ Added: {job_data['title']} at {job_data['company']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to scrape: {str(e)}")
    
    else:
        with st.form("batch_job_form", clear_on_submit=True):
            urls_text = st.text_area(
                "Paste job URLs (one per line)",
                placeholder="https://linkedin.com/jobs/...\nhttps://indeed.com/...",
                height=150,
                key="batch_urls"
            )
            submit = st.form_submit_button("➕ Add All URLs", use_container_width=True)
        
        if submit and urls_text:
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            if not urls:
                st.warning("No valid URLs found")
            else:
                progress_bar = st.progress(0)
                scraper = JobScraper()
                success_count = 0
                
                for i, url in enumerate(urls):
                    try:
                        job_data = scraper.scrape_job(url)
                        st.session_state.jobs.append(job_data)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Failed to scrape {url}: {e}")
                    progress_bar.progress((i + 1) / len(urls))
                
                st.success(f"✅ Added {success_count}/{len(urls)} jobs!")
                st.rerun()
    
    # Display added jobs
    if st.session_state.jobs:
        st.markdown("---")
        st.markdown(f"#### 📋 Jobs to Process ({len(st.session_state.jobs)} total)")
        
        # Create columns for job cards
        for i, job in enumerate(st.session_state.jobs, 1):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div class="job-card">
                    <b>{i}. {job['title']}</b> at {job['company']}<br>
                    <small>{job['url']}</small><br>
                    <small>Description: {len(job['description'])} chars</small>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"remove_{i}_{job['url'][:20]}", help="Remove this job"):
                    st.session_state.jobs.pop(i-1)
                    st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Step 1", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            if st.button("Generate Tailored Resumes →", type="primary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
    else:
        st.warning("⚠️ No jobs added yet. Add at least one job URL above.")
        
        # Still show back button even with no jobs
        if st.button("← Back to Step 1"):
            st.session_state.current_step = 1
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_3_generate_resumes():
    """Step 3: Generate tailored resumes"""
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown("### ✨ Step 3: Generate Tailored Resumes")
    
    if not check_api_key():
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if not st.session_state.jobs:
        st.warning("⚠️ No jobs added. Please go back to Step 2.")
        if st.button("← Back to Step 2", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if not st.session_state.resume_data:
        st.warning("⚠️ No resume uploaded. Please go back to Step 1.")
        if st.button("← Back to Step 1", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Show summary before generation
    st.info(f"📄 Resume: {len(st.session_state.resume_data.get('lines', []))} lines parsed")
    st.info(f"💼 Jobs to process: {len(st.session_state.jobs)}")
    
    if st.button("🚀 Start Generation", type="primary", use_container_width=True):
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            tailor = ResumeTailor()
            generator = ResumeGenerator()
            
            results = []
            total_jobs = len(st.session_state.jobs)
            
            for i, job in enumerate(st.session_state.jobs, 1):
                progress_text.text(f"📝 Processing job {i}/{total_jobs}: {job['title']} at {job['company']}...")
                
                try:
                    # Tailor the resume
                    tailored_text = tailor.tailor_resume(st.session_state.resume_data, job)
                    
                    # Generate files
                    base_filename = f"resume_{i:02d}"
                    files = generator.generate_both_formats(tailored_text, job, base_filename)
                    
                    results.append({
                        'job': job,
                        'tailored_text': tailored_text,
                        'files': files,
                        'success': True
                    })
                    
                except Exception as e:
                    st.error(f"❌ Failed job {i}: {str(e)}")
                    results.append({
                        'job': job,
                        'error': str(e),
                        'success': False
                    })
                
                progress_bar.progress(i / total_jobs)
            
            st.session_state.tailored_resumes = results
            progress_text.text(f"✅ Generation complete! {sum(1 for r in results if r['success'])}/{total_jobs} successful")
            
            if any(r['success'] for r in results):
                st.balloons()
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Critical error during generation: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    # Navigation buttons when not generating
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Step 2", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    with col2:
        if st.session_state.tailored_resumes and st.button("🔄 Reset & Start Over", use_container_width=True):
            st.session_state.resume_data = None
            st.session_state.jobs = []
            st.session_state.tailored_resumes = []
            st.session_state.current_step = 1
            st.rerun()
    
    # Display results
    if st.session_state.tailored_resumes:
        st.markdown("---")
        st.markdown("### 📥 Download Your Tailored Resumes")
        
        for i, result in enumerate(st.session_state.tailored_resumes, 1):
            with st.expander(f"📄 {result['job']['title']} at {result['job']['company']}", expanded=True):
                if result['success']:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with open(result['files']['docx'], 'rb') as f:
                            st.download_button(
                                label="📄 Download DOCX",
                                data=f,
                                file_name=result['files']['docx_name'],
                                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                use_container_width=True
                            )
                    
                    with col2:
                        with open(result['files']['pdf'], 'rb') as f:
                            st.download_button(
                                label="📑 Download PDF",
                                data=f,
                                file_name=result['files']['pdf_name'],
                                mime='application/pdf',
                                use_container_width=True
                            )
                    
                    # Preview toggle
                    if st.checkbox(f"Preview tailored resume {i}", key=f"preview_{i}"):
                        st.text_area("Tailored Resume", result['tailored_text'], height=400)
                else:
                    st.error(f"❌ Failed to generate: {result.get('error', 'Unknown error')}")
        
        # Reset button
        if st.button("🔄 Start Over", type="secondary"):
            st.session_state.resume_data = None
            st.session_state.jobs = []
            st.session_state.tailored_resumes = []
            st.session_state.current_step = 1
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    initialize_session()
    
    # Header
    st.markdown('<div class="main-header">📄 AI Resume Tailor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automatically tailor your resume for multiple job applications using AI</div>', unsafe_allow_html=True)
    
    # Progress indicator
    st.progress(st.session_state.current_step / 3)
    
    # Show current step
    if st.session_state.current_step == 1:
        step_1_upload_resume()
    elif st.session_state.current_step == 2:
        step_2_add_jobs()
    elif st.session_state.current_step == 3:
        step_3_generate_resumes()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        Powered by Groq AI • Free tier: 20 requests/min<br>
        <a href="https://console.groq.com/keys" target="_blank">Get your free API key</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()