from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import List, Dict

def scrape_glassdoor_jobs(keyword: str, num_jobs: int, slp_time: int = 3, progress=None) -> List[Dict]:
    """
    Scrape jobs from Glassdoor using Selenium.
    
    Args:
        keyword: Job role to search for (e.g., "Data Science", "Software Engineer")
        num_jobs: Number of jobs to scrape
        slp_time: Sleep time between page loads
    
    Returns:
        List of job dictionaries
    """
    print(f"Starting Glassdoor scrape for '{keyword}' - Target: {num_jobs} jobs")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1000")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add user agent to avoid detection
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    jobs = []
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1200, 1000)
        
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword.replace(' ', '%20')}"
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        while len(jobs) < num_jobs:
            try:
                # Wait for job cards to load
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.JobCard_jobCardWrapper__vX29z"))
                )
                print(f"Found {len(job_cards)} job cards on current page")
            except TimeoutException:
                print("⚠️ No job cards found. Structure may have changed.")
                break

            for i, card in enumerate(job_cards):
                if len(jobs) >= num_jobs:
                    break

                try:
                    print(f"Processing job card {i+1}/{len(job_cards)}")
                    
                    # --- Job Title & URL ---
                    job_title = "N/A"
                    job_url = "N/A"
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='job-title']")
                        job_title = title_elem.text.strip()
                        job_url = title_elem.get_attribute("href")
                        print(f"  Title: {job_title}")
                    except Exception as e:
                        print(f"  Error getting title: {e}")
                        job_title, job_url = "N/A", "N/A"

                    # --- Company Name ---
                    company_name = "N/A"
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, "span.EmployerProfile_compactEmployerName__9MGcV")
                        company_name = company_elem.text.strip()
                        print(f"  Company: {company_name}")
                    except Exception as e:
                        print(f"  Error getting company: {e}")
                        company_name = "N/A"

                    # --- Location ---
                    location = "N/A"
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, "div[data-test='emp-location']")
                        location = location_elem.text.strip()
                        print(f"  Location: {location}")
                    except Exception as e:
                        print(f"  Error getting location: {e}")
                        location = "N/A"

                    # --- Job Description (simplified approach) ---
                    job_description = f"View full job description for {job_title} at {company_name} on Glassdoor"

                    # Only add job if we have at least title or company
                    if job_title != "N/A" or company_name != "N/A":
                        job_data = {
                            "job_title": job_title,
                            "company_name": company_name,
                            "location": location,
                            "job_description": job_description,
                            "source_url": job_url,
                            "sources": ["glassdoor"]
                        }
                        jobs.append(job_data)
                        print(f"📝 Collected job data: {job_title} at {company_name}")
                        
                        # Save job to database in real-time
                        try:
                            saved = save_single_job_to_db(job_data)
                            if saved:
                                print(f"✅ Added job {len(jobs)}: {job_title} at {company_name} (saved to DB)")
                            else:
                                print(f"⚠️ Job {len(jobs)}: {job_title} at {company_name} (duplicate, not saved)")
                        except Exception as e:
                            print(f"❌ Error saving job to DB: {e}")
                            import traceback
                            traceback.print_exc()
                        
                        # Update progress
                        if progress:
                            progress.update("scraping", 20 + (len(jobs) * 60 // num_jobs), 100, 
                                         f"Found {len(jobs)} jobs so far...")
                    else:
                        print(f"❌ Skipping job card {i+1} - no valid title or company")

                except Exception as e:
                    print(f"❌ Error processing job card {i+1}: {str(e)[:100]}...")
                    continue

            # --- Next page ---
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[data-test='pagination-next']")
                if next_button.is_enabled():
                    print("Moving to next page...")
                    next_button.click()
                    time.sleep(slp_time)
                else:
                    print("No more pages available")
                    break
            except NoSuchElementException:
                print("Next button not found, stopping")
                break

    except Exception as e:
        print(f"Error during Glassdoor scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    print(f"✅ Glassdoor scraping completed. Found {len(jobs)} jobs")
    return jobs


def save_single_job_to_db(job_data: Dict) -> bool:
    """
    Save a single job to the database with duplicate prevention.
    Returns True if job was saved, False if it was a duplicate.
    """
    try:
        from ..models import Job, Company
        from .utils import fingerprint, normalize_text
        from django.db import transaction
        
        # Create fingerprint for duplicate detection
        job_fingerprint = fingerprint(
            normalize_text(job_data.get("job_title", "")),
            normalize_text(job_data.get("company_name", "")),
            normalize_text(job_data.get("location", ""))
        )
        
        with transaction.atomic():
            # Check if job already exists
            existing_job = Job.objects.filter(fingerprint=job_fingerprint).first()
            if existing_job:
                # Update sources if needed
                if "glassdoor" not in existing_job.sources:
                    existing_job.sources.append("glassdoor")
                    existing_job.save()
                return False  # Duplicate, not saved as new
            
            # Get or create company
            company_name = job_data.get("company_name", "Unknown Company")
            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={'name': company_name}
            )
            
            # Create new job
            job = Job.objects.create(
                title=job_data.get("job_title", "N/A"),
                company=company,
                location=job_data.get("location", "N/A"),
                description=job_data.get("job_description", "N/A"),
                source_url=job_data.get("source_url", ""),
                sources=["glassdoor"],
                fingerprint=job_fingerprint
            )
            
            return True  # Successfully saved
            
    except Exception as e:
        print(f"Error saving job to database: {e}")
        return False
