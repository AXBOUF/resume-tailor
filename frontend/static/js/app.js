// AI Resume Tailor - Interactive Web Application
// Smooth animations and antigravity effects

// Initialize Lucide icons
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initApp();
});

// Global state
const state = {
    resumeFile: null,
    parsedResume: null,
    jobUrls: [],
    scrapedJobs: [],
    generatedFiles: [],
    currentStep: 1
};

// Initialize application
function initApp() {
    initParticles();
    initScrollAnimations();
    initNavigation();
    initUploadZone();
    initUrlManager();
    initScrapeButton();
    initGenerateButton();
}

// Create floating particles (antigravity effect)
function initParticles() {
    const container = document.getElementById('particles');
    const particleCount = 25;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 15}s`;
        particle.style.animationDuration = `${10 + Math.random() * 10}s`;
        container.appendChild(particle);
    }
}

// GSAP Scroll animations
function initScrollAnimations() {
    gsap.registerPlugin(ScrollTrigger);
    
    // Hero entrance animations
    const heroTl = gsap.timeline({ delay: 0.3 });
    
    heroTl.from('.hero-badge', {
        opacity: 0,
        y: 20,
        duration: 0.8,
        ease: 'power3.out'
    })
    .from('.hero h1', {
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    }, '-=0.5')
    .from('.hero p', {
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    }, '-=0.5')
    .from('.hero-buttons', {
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    }, '-=0.5')
    .from('.scroll-indicator', {
        opacity: 0,
        duration: 1,
        ease: 'power2.out'
    }, '-=0.3');
    
    // Step cards animation
    gsap.utils.toArray('.step-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 40,
            duration: 0.8,
            delay: i * 0.15,
            ease: 'power3.out'
        });
    });
    
    // Features animation
    gsap.utils.toArray('.feature-item').forEach((item, i) => {
        gsap.from(item, {
            scrollTrigger: {
                trigger: item,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            opacity: 0,
            y: 30,
            duration: 0.6,
            delay: i * 0.1,
            ease: 'power3.out'
        });
    });
    
    // Parallax effect on background
    gsap.to('.bg-gradient', {
        scrollTrigger: {
            trigger: 'body',
            start: 'top top',
            end: 'bottom bottom',
            scrub: 1
        },
        y: 100,
        ease: 'none'
    });
}

// Navigation visibility on scroll
function initNavigation() {
    const nav = document.getElementById('navbar');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            nav.classList.add('visible');
        } else {
            nav.classList.remove('visible');
        }
        
        lastScroll = currentScroll;
    }, { passive: true });
    
    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                gsap.to(window, {
                    duration: 1,
                    scrollTo: { y: target, offsetY: 80 },
                    ease: 'power3.inOut'
                });
            }
        });
    });
}

// Upload zone functionality
function initUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('resumeFile');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    
    uploadZone.addEventListener('click', () => fileInput.click());
    
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    async function handleFileUpload(file) {
        const allowedTypes = ['.pdf', '.docx', '.doc'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExt)) {
            showToast('Invalid file type. Please upload PDF or DOCX.', 'error');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            showToast('File too large. Maximum size is 10MB.', 'error');
            return;
        }
        
        state.resumeFile = file;
        fileName.textContent = file.name;
        fileInfo.style.display = 'flex';
        uploadZone.style.display = 'none';
        
        showToast('Resume uploaded successfully!', 'success');
        
        // Animate the step card
        gsap.from(fileInfo, {
            opacity: 0,
            scale: 0.9,
            duration: 0.4,
            ease: 'back.out(1.7)'
        });
        
        // Parse resume
        await parseResume(file);
    }
}

// Parse resume via API
async function parseResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showToast('Parsing resume...', 'info');
        
        const response = await fetch('/api/parse-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to parse resume');
        }
        
        const data = await response.json();
        state.parsedResume = data.data;
        
        showToast(`Resume parsed! Found ${Object.keys(data.data).length} sections.`, 'success');
        
        // Animate progress to next step
        gsap.to(window, {
            duration: 0.8,
            scrollTo: { y: '.step-card[data-step="2"]', offsetY: 100 },
            ease: 'power2.inOut'
        });
        
    } catch (error) {
        showToast('Error parsing resume: ' + error.message, 'error');
    }
}

// URL manager functionality
function initUrlManager() {
    const urlList = document.getElementById('urlList');
    const addBtn = document.getElementById('addUrl');
    
    addBtn.addEventListener('click', () => {
        const group = document.createElement('div');
        group.className = 'url-input-group';
        group.innerHTML = `
            <input type="url" placeholder="https://jobs.company.com/job-id" class="job-url">
            <button class="btn-icon remove-url" title="Remove">
                <i data-lucide="x" style="width:20px;height:20px;"></i>
            </button>
        `;
        
        urlList.appendChild(group);
        lucide.createIcons();
        
        // Animate new input
        gsap.from(group, {
            opacity: 0,
            x: -20,
            duration: 0.3,
            ease: 'power2.out'
        });
        
        // Add remove functionality
        group.querySelector('.remove-url').addEventListener('click', () => {
            gsap.to(group, {
                opacity: 0,
                x: 20,
                duration: 0.2,
                onComplete: () => group.remove()
            });
        });
    });
}

// Scrape jobs button
function initScrapeButton() {
    const scrapeBtn = document.getElementById('scrapeBtn');
    
    scrapeBtn.addEventListener('click', async () => {
        const inputs = document.querySelectorAll('.job-url');
        const urls = Array.from(inputs)
            .map(input => input.value.trim())
            .filter(url => url.length > 0);
        
        if (urls.length === 0) {
            showToast('Please add at least one job URL', 'error');
            return;
        }
        
        try {
            scrapeBtn.disabled = true;
            scrapeBtn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Scraping...';
            lucide.createIcons();
            
            const response = await fetch('/api/scrape-jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ urls })
            });
            
            const data = await response.json();
            
            // Poll for status
            await pollJobStatus(data.job_id, 'scraping');
            
        } catch (error) {
            showToast('Error scraping jobs: ' + error.message, 'error');
            scrapeBtn.disabled = false;
            scrapeBtn.innerHTML = '<i data-lucide="search"></i> Scrape Job Details';
            lucide.createIcons();
        }
    });
}

// Generate resumes button
function initGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    
    generateBtn.addEventListener('click', async () => {
        if (!state.parsedResume) {
            showToast('Please upload and parse your resume first', 'error');
            return;
        }
        
        if (state.scrapedJobs.length === 0) {
            showToast('Please scrape job details first', 'error');
            return;
        }
        
        // Show progress container
        document.getElementById('progressContainer').classList.add('active');
        generateBtn.style.display = 'none';
        
        try {
            const formData = new FormData();
            formData.append('resume_file', 'output/resume_parsed.json');
            formData.append('jobs_file', 'output/jobs_scraped.json');
            
            const response = await fetch('/api/tailor-resume', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Poll for status
            await pollJobStatus(data.job_id, 'tailoring');
            
        } catch (error) {
            showToast('Error generating resumes: ' + error.message, 'error');
            generateBtn.style.display = 'block';
        }
    });
}

// Poll job status
async function pollJobStatus(jobId, type) {
    const progressCircle = document.getElementById('progressCircle');
    const progressText = document.getElementById('progressText');
    const progressTitle = document.getElementById('progressTitle');
    const progressStatus = document.getElementById('progressStatus');
    const circumference = 2 * Math.PI * 52;
    
    const checkStatus = async () => {
        try {
            const response = await fetch(`/api/job-status/${jobId}`);
            const data = await response.json();
            
            // Update progress
            const offset = circumference - (data.progress / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
            progressText.textContent = `${data.progress}%`;
            
            // Update status text
            if (type === 'scraping') {
                progressTitle.textContent = 'Scraping Jobs...';
                progressStatus.textContent = `Found ${data.jobs?.length || 0} jobs`;
            } else {
                progressTitle.textContent = 'Generating Resumes...';
                progressStatus.textContent = `Processing with AI...`;
            }
            
            if (data.status === 'completed') {
                if (type === 'scraping') {
                    state.scrapedJobs = data.jobs;
                    document.getElementById('progressContainer').classList.remove('active');
                    document.getElementById('scrapeBtn').disabled = false;
                    document.getElementById('scrapeBtn').innerHTML = '<i data-lucide="check"></i> Jobs Scraped!';
                    lucide.createIcons();
                    showToast(`Successfully scraped ${data.jobs.length} jobs!`, 'success');
                    
                    // Scroll to step 3
                    gsap.to(window, {
                        duration: 0.8,
                        scrollTo: { y: '.step-card[data-step="3"]', offsetY: 100 },
                        ease: 'power2.inOut'
                    });
                } else {
                    state.generatedFiles = data.files;
                    showResults(data.files);
                }
            } else if (data.status === 'error') {
                showToast('Error: ' + data.errors[0], 'error');
                if (type === 'scraping') {
                    document.getElementById('scrapeBtn').disabled = false;
                    document.getElementById('scrapeBtn').textContent = 'Scrape Job Details';
                } else {
                    document.getElementById('generateBtn').style.display = 'block';
                }
            } else {
                setTimeout(checkStatus, 1000);
            }
        } catch (error) {
            showToast('Error checking status: ' + error.message, 'error');
        }
    };
    
    checkStatus();
}

// Show generated results
function showResults(files) {
    const container = document.getElementById('resultsContainer');
    const grid = document.getElementById('resultsGrid');
    const progressContainer = document.getElementById('progressContainer');
    
    progressContainer.classList.remove('active');
    container.classList.add('active');
    
    grid.innerHTML = files.map(file => `
        <div class="result-card">
            <h4>${file.company}</h4>
            <p>${file.title}</p>
            <div class="result-actions">
                <a href="/api/download/${file.text}" class="btn btn-primary btn-small" download>
                    <i data-lucide="download" style="width:16px;height:16px;"></i>
                    Download
                </a>
                ${file.job_url ? `
                <a href="${file.job_url}" target="_blank" class="btn btn-secondary btn-small">
                    <i data-lucide="external-link" style="width:16px;height:16px;"></i>
                    Job Post
                </a>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    lucide.createIcons();
    
    // Animate results
    gsap.from('.result-card', {
        opacity: 0,
        y: 30,
        duration: 0.5,
        stagger: 0.1,
        ease: 'power2.out'
    });
    
    showToast(`Generated ${files.length} tailored resumes!`, 'success');
}

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'check-circle',
        error: 'x-circle',
        info: 'info'
    };
    
    toast.innerHTML = `
        <i data-lucide="${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
