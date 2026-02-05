from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import html2text
import re
import time
from typing import Dict, Optional
from urllib.parse import urlparse

class JobScraper:
    """Scrape job descriptions from various job posting URLs"""
    
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = True
        
        # Site-specific selectors for job descriptions
        self.site_selectors = {
            'linkedin.com': {
                'description': ['.description__text', '.jobs-description__content', '[data-test-id="job-description"]', '.job-details-jobs-unified-description__content'],
                'title': ['.job-details-jobs-unified-top-card__job-title', 'h1', '.topcard__title'],
                'company': ['.job-details-jobs-unified-top-card__company-name', '.topcard__org-name-link']
            },
            'indeed.com': {
                'description': ['#jobDescriptionText', '.jobsearch-jobDescriptionText', '[data-testid="jobDescriptionText"]'],
                'title': ['.jobsearch-JobInfoHeader-title', 'h1', '[data-testid="jobsearch-JobInfoHeader-title"]'],
                'company': ['.jobsearch-JobInfoHeader-companyName', '[data-testid="jobsearch-JobInfoHeader-companyName"]']
            },
            'greenhouse.io': {
                'description': ['.job-description', '#content', '.app-body'],
                'title': ['.app-title', 'h1', '.job-title'],
                'company': ['.company-name', '.header-company-name']
            },
            'lever.co': {
                'description': ['.job-description', '.posting-description', '[data-qa="job-description"]'],
                'title': ['.posting-headline', 'h2', '.job-title'],
                'company': ['.main-header-title']
            },
            'workday.com': {
                'description': ['.job-description', '[data-automation-id="jobDescription"]', '.wd-JobDescription'],
                'title': ['h1', '[data-automation-id="jobPostingHeader"]'],
                'company': ['.company-name']
            },
            'ashbyhq.com': {
                'description': ['.job-description', '[data-testid="job-description"]', '.description'],
                'title': ['h1', '.job-title'],
                'company': ['.company-name']
            }
        }
    
    def scrape_job(self, url: str) -> Dict[str, str]:
        """Scrape job description from URL"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                # Navigate to URL with timeout
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for page to load
                time.sleep(3)
                
                # Get page content
                html_content = page.content()
                browser.close()
                
                # Parse the content
                return self._extract_job_info(url, html_content)
                
        except Exception as e:
            return {
                'url': url,
                'title': 'Error',
                'company': 'Unknown',
                'description': f'Failed to scrape: {str(e)}',
                'error': str(e)
            }
    
    def _extract_job_info(self, url: str, html_content: str) -> Dict[str, str]:
        """Extract job information from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Detect site
        domain = self._get_domain(url)
        selectors = self.site_selectors.get(domain, {})
        
        # Extract job description
        description = self._extract_with_selectors(soup, selectors.get('description', []))
        
        # If no specific selectors matched, try generic extraction
        if not description:
            description = self._generic_description_extraction(soup)
        
        # Clean up description
        description = self._clean_description(description)
        
        # Extract title and company
        title = self._extract_with_selectors(soup, selectors.get('title', []))
        if not title:
            title = self._extract_title_generic(soup)
        
        company = self._extract_with_selectors(soup, selectors.get('company', []))
        if not company:
            company = self._extract_company_generic(soup, domain)
        
        return {
            'url': url,
            'title': title or 'Unknown Position',
            'company': company or 'Unknown Company',
            'description': description,
            'domain': domain
        }
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. and extract main domain
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Match against known domains
        for known_domain in self.site_selectors.keys():
            if known_domain in domain:
                return known_domain
        
        return domain
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: list) -> str:
        """Try to extract text using CSS selectors"""
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    text = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if text:
                        return text
            except:
                continue
        return ''
    
    def _generic_description_extraction(self, soup: BeautifulSoup) -> str:
        """Generic method to extract job description"""
        # Common job description containers
        potential_containers = [
            'article', 'main', '[role="main"]',
            '.content', '#content', '.main-content',
            '.job-details', '.position-details',
            '[data-testid*="description"]', '[data-testid*="job"]'
        ]
        
        for container in potential_containers:
            try:
                elements = soup.select(container)
                if elements:
                    text = elements[0].get_text(separator='\n', strip=True)
                    # Check if it looks like a job description (reasonable length)
                    if len(text) > 500:
                        return text
            except:
                continue
        
        # Fallback: extract from body but exclude header/footer/nav
        body = soup.find('body')
        if body:
            # Remove common non-content elements
            for tag in body.find_all(['header', 'footer', 'nav', 'aside', 'script', 'style']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)
        
        return soup.get_text(separator='\n', strip=True)
    
    def _clean_description(self, text: str) -> str:
        """Clean up extracted job description"""
        if not text:
            return text
        
        # Convert HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove common footer text patterns
        footer_patterns = [
            r'Apply.*?Now',
            r'Save.*?job',
            r'Share this job',
            r'Report this job',
            r'Posted \d+ days? ago',
            r'\d+ applicants?',
        ]
        
        for pattern in footer_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_title_generic(self, soup: BeautifulSoup) -> str:
        """Generic method to extract job title"""
        # Try h1 tags
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()
        
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove site name if present
            title = re.sub(r'[\|\-–—].*$', '', title).strip()
            return title
        
        return ''
    
    def _extract_company_generic(self, soup: BeautifulSoup, domain: str) -> str:
        """Generic method to extract company name"""
        # Try meta tags
        meta_employer = soup.find('meta', {'name': 'employer'})
        if meta_employer:
            return meta_employer.get('content', '').strip()
        
        # Try to extract from domain for common job boards
        if 'greenhouse' in domain:
            # Greenhouse URLs often contain company name
            match = re.search(r'boards\.greenhouse\.io/([^/]+)', str(soup))
            if match:
                return match.group(1).replace('-', ' ').title()
        
        if 'lever' in domain:
            # Lever URLs: jobs.lever.co/company-name
            match = re.search(r'jobs\.lever\.co/([^/]+)', str(soup))
            if match:
                return match.group(1).replace('-', ' ').title()
        
        # Extract from page content - look for common patterns
        company_patterns = [
            r'at\s+([A-Z][A-Za-z0-9\s&]+)(?:\s+\||\s+-|\s+—|\s*\n|$)',
            r'Join\s+([A-Z][A-Za-z0-9\s&]+)',
            r'About\s+([A-Z][A-Za-z0-9\s&]+)',
        ]
        
        text = soup.get_text()
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Extract from domain
        return domain.split('.')[0].replace('-', ' ').title()