import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_glassdoor(keyword: str, location: str, num_pages: int = 1, max_jobs: int = 50):
    print(f"Starting Glassdoor scrape for '{keyword}' in '{location}' using requests")
    
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # First, get the main page to establish session
        print("Getting Glassdoor main page...")
        main_response = session.get("https://www.glassdoor.com/Job/index.htm")
        print(f"Main page status: {main_response.status_code}")
        
        if main_response.status_code != 200:
            print(f"Failed to access Glassdoor main page: {main_response.status_code}")
            return []
        
        # Try to search for jobs using a direct search URL
        search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword.replace(' ', '+')}&locT=C&locId=1&jobType=&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100&cityId=-1"
        print(f"Searching with URL: {search_url}")
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(2, 4))
        
        search_response = session.get(search_url)
        print(f"Search response status: {search_response.status_code}")
        
        if search_response.status_code != 200:
            print(f"Search failed with status: {search_response.status_code}")
            return []
        
        # Parse the response
        soup = BeautifulSoup(search_response.content, 'html.parser')
        
        # Look for job listings
        jobs = []
        
        # Multiple selectors to try for job listings
        job_selectors = [
            'li[data-adv-type="GENERAL"]',
            'div[data-test="job-listing"]',
            'article[data-test="job-card"]',
            '.jobContainer',
            '.jobListing',
            '[data-test*="job"]'
        ]
        
        job_elements = []
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} job elements with selector: {selector}")
                job_elements = elements
                break
        
        if not job_elements:
            print("No job elements found with any selector")
            print("Page title:", soup.title.string if soup.title else "No title")
            
            # Save the HTML for debugging
            with open("glassdoor_debug.html", "w", encoding="utf-8") as f:
                f.write(search_response.text)
            print("Saved page HTML to glassdoor_debug.html for debugging")
            return []
        
        # Process job elements
        for idx, job_element in enumerate(job_elements[:max_jobs]):
            try:
                print(f"Processing job {idx + 1}")
                
                job = {
                    "company_name": "N/A",
                    "job_title": "N/A", 
                    "location": "N/A",
                    "job_description": "N/A",
                    "salary": "N/A",
                    "source_url": search_url,
                }
                
                # Try to extract company name
                company_selectors = [
                    '[data-test="employer-name"]',
                    '.companyName',
                    '[class*="companyName"]',
                    'h3[class*="company"]',
                    'span[class*="company"]'
                ]
                
                for selector in company_selectors:
                    element = job_element.select_one(selector)
                    if element and element.get_text(strip=True):
                        job["company_name"] = element.get_text(strip=True)
                        break
                
                # Try to extract job title
                title_selectors = [
                    '[data-test="job-title"]',
                    '.jobTitle',
                    '[class*="jobTitle"]',
                    'h2[class*="job"]',
                    'a[class*="job"]'
                ]
                
                for selector in title_selectors:
                    element = job_element.select_one(selector)
                    if element and element.get_text(strip=True):
                        job["job_title"] = element.get_text(strip=True)
                        break
                
                # Try to extract location
                location_selectors = [
                    '[data-test="job-location"]',
                    '.location',
                    '[class*="location"]'
                ]
                
                for selector in location_selectors:
                    element = job_element.select_one(selector)
                    if element and element.get_text(strip=True):
                        job["location"] = element.get_text(strip=True)
                        break
                
                # Try to extract salary
                salary_selectors = [
                    '[data-test="salary"]',
                    '.salary',
                    '[class*="salary"]'
                ]
                
                for selector in salary_selectors:
                    element = job_element.select_one(selector)
                    if element and element.get_text(strip=True):
                        job["salary"] = element.get_text(strip=True)
                        break
                
                # Only add if we got meaningful data
                if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                    jobs.append(job)
                    print(f"Added job: {job['job_title']} at {job['company_name']}")
                else:
                    print(f"Job {idx + 1} had insufficient data")
                
            except Exception as e:
                print(f"Error processing job {idx + 1}: {e}")
                continue
        
        print(f"Scraping completed. Found {len(jobs)} jobs")
        return jobs
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return []
