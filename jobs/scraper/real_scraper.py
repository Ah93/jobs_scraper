import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import quote
from typing import List, Dict

def scrape_real_jobs(keyword: str, location: str, max_jobs: int = 50) -> List[Dict]:
    """
    Try to scrape real jobs from more accessible sources.
    """
    print(f"Attempting to scrape real jobs for '{keyword}' in '{location}'")
    
    scrapers = [
        ("GitHub Jobs", scrape_github_jobs),
        ("Stack Overflow Jobs", scrape_stackoverflow_jobs),
        ("Remote.co", scrape_remote_co),
        ("FlexJobs", scrape_flexjobs),
        ("AngelList (Wellfound)", scrape_wellfound),
        ("Built In", scrape_builtin),
        ("Hacker News Jobs", scrape_hackernews_jobs),
        ("DevJobs", scrape_devjobs)
    ]
    
    all_jobs = []
    
    for site_name, scraper_func in scrapers:
        try:
            print(f"Trying {site_name}...")
            jobs = scraper_func(keyword, location, max_jobs)
            if jobs:
                print(f"✅ {site_name}: Found {len(jobs)} jobs")
                all_jobs.extend(jobs)
                if len(all_jobs) >= max_jobs:
                    break
            else:
                print(f"❌ {site_name}: No jobs found")
        except Exception as e:
            print(f"❌ {site_name}: Error - {e}")
            continue
    
    # Remove duplicates and limit
    unique_jobs = []
    seen_titles = set()
    
    for job in all_jobs:
        title_key = f"{job.get('job_title', '')}_{job.get('company_name', '')}"
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_jobs.append(job)
            if len(unique_jobs) >= max_jobs:
                break
    
    print(f"Total unique jobs found: {len(unique_jobs)}")
    return unique_jobs

def get_realistic_headers():
    """Get realistic headers for scraping"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }

def scrape_github_jobs(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape GitHub Jobs (if available)"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # GitHub Jobs was discontinued, but let's try the API
        url = f"https://jobs.github.com/positions.json?description={quote(keyword)}&location={quote(location)}"
        time.sleep(random.uniform(1, 3))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = []
            for job in jobs_data[:max_jobs]:
                jobs.append({
                    "job_title": job.get("title", "N/A"),
                    "company_name": job.get("company", "N/A"),
                    "location": job.get("location", "N/A"),
                    "job_description": job.get("description", "N/A"),
                    "salary": "N/A",
                    "source_url": job.get("url", "https://jobs.github.com")
                })
            return jobs
    except:
        pass
    
    return []

def scrape_stackoverflow_jobs(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape Stack Overflow Jobs"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://stackoverflow.com/jobs?q={quote(keyword)}&l={quote(location)}"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://stackoverflow.com/jobs"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h2 a, .job-title a, h3 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://stackoverflow.com{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name, .employer')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = element.select_one('.location, .job-location')
                    if location_elem:
                        job["location"] = location_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_remote_co(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape Remote.co"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://remote.co/remote-jobs/{keyword.replace(' ', '-')}/"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "Remote",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://remote.co"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h3 a, .job-title a, h2 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://remote.co{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_flexjobs(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape FlexJobs (free section)"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://www.flexjobs.com/search?search={quote(keyword)}&location={quote(location)}"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://www.flexjobs.com"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h3 a, .job-title a, h2 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://www.flexjobs.com{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = element.select_one('.location, .job-location')
                    if location_elem:
                        job["location"] = location_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_wellfound(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape Wellfound (formerly AngelList)"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://wellfound.com/role/l/{keyword.replace(' ', '-')}"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://wellfound.com"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h3 a, .job-title a, h2 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://wellfound.com{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = element.select_one('.location, .job-location')
                    if location_elem:
                        job["location"] = location_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_builtin(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape Built In (tech jobs)"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://builtin.com/jobs?search={quote(keyword)}&location={quote(location)}"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://builtin.com"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h3 a, .job-title a, h2 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://builtin.com{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = element.select_one('.location, .job-location')
                    if location_elem:
                        job["location"] = location_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_hackernews_jobs(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape Hacker News Jobs"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = "https://news.ycombinator.com/jobs"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.athing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://news.ycombinator.com/jobs"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('.titleline a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = title_elem.get('href')
                    
                    # Extract company (usually in the title)
                    if job["job_title"] != "N/A":
                        # Try to extract company from title
                        title = job["job_title"]
                        if " at " in title:
                            parts = title.split(" at ")
                            if len(parts) == 2:
                                job["job_title"] = parts[0].strip()
                                job["company_name"] = parts[1].strip()
                    
                    if job["job_title"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

def scrape_devjobs(keyword: str, location: str, max_jobs: int) -> List[Dict]:
    """Scrape DevJobs"""
    headers = get_realistic_headers()
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        url = f"https://devjobs.com/jobs?q={quote(keyword)}&l={quote(location)}"
        time.sleep(random.uniform(2, 4))
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = []
            
            job_elements = soup.select('.job, .job-card, .job-listing')
            
            for element in job_elements[:max_jobs]:
                try:
                    job = {
                        "job_title": "N/A",
                        "company_name": "N/A",
                        "location": "N/A",
                        "job_description": "N/A",
                        "salary": "N/A",
                        "source_url": "https://devjobs.com"
                    }
                    
                    # Extract title
                    title_elem = element.select_one('h3 a, .job-title a, h2 a')
                    if title_elem:
                        job["job_title"] = title_elem.get_text(strip=True)
                        if title_elem.get('href'):
                            job["source_url"] = f"https://devjobs.com{title_elem.get('href')}"
                    
                    # Extract company
                    company_elem = element.select_one('.company, .company-name')
                    if company_elem:
                        job["company_name"] = company_elem.get_text(strip=True)
                    
                    # Extract location
                    location_elem = element.select_one('.location, .job-location')
                    if location_elem:
                        job["location"] = location_elem.get_text(strip=True)
                    
                    if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                        jobs.append(job)
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []
