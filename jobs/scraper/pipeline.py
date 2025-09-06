import time
from typing import List, Dict
from django.db import transaction
from .driver import build_driver
from .glassdoor import scrape_glassdoor
from .utils import fingerprint, normalize_text
from ..models import Job, Company


def run_scrape_pipeline(platform: str, role_name: str, limit: int, location: str = "New York, NY", progress=None) -> int:
    """
    Main pipeline function to scrape jobs from the specified platform.
    
    Args:
        platform: The platform to scrape from (glassdoor, indeed, linkedin)
        role_name: The job role to search for
        limit: Maximum number of jobs to scrape
        location: Location to search in (for Indeed)
        progress: Progress tracker object
        
    Returns:
        Number of jobs added/updated
    """
    print(f"Starting scrape pipeline for {platform} with limit {limit}")
    scraped_jobs = []
    
    try:
        if progress:
            progress.update("scraping", 10, 100, f"Starting {platform} scraper for '{role_name}'...")
        
        if platform == "glassdoor":
            print(f"Calling Glassdoor Selenium scraper for '{role_name}'...")
            scraped_jobs = scrape_glassdoor_from_role(role_name, limit, progress)
            print(f"Glassdoor scraper returned {len(scraped_jobs)} jobs")
        elif platform == "indeed":
            print(f"Calling Indeed scraper for '{role_name}' in '{location}'...")
            scraped_jobs = scrape_indeed_from_role(role_name, location, limit, progress)
            print(f"Indeed scraper returned {len(scraped_jobs)} jobs")
        elif platform == "linkedin":
            scraped_jobs = scrape_linkedin_from_url(role_name, limit)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        if progress:
            progress.update("processing", 70, 100, f"Processing {len(scraped_jobs)} jobs...")
            
        # Save jobs to database
        if scraped_jobs:
            saved_count = save_jobs_to_database(scraped_jobs, platform)
            print(f"Saved {saved_count} new jobs to database")
        else:
            saved_count = 0
            
        if progress:
            progress.update("complete", 100, 100, f"Scraping complete. {saved_count} jobs available.")
        
        return saved_count
        
    except Exception as e:
        print(f"Error in scraping pipeline: {e}")
        import traceback
        traceback.print_exc()
        if progress:
            progress.error(f"Scraping failed: {str(e)}")
        return 0


def scrape_glassdoor_from_role(role_name: str, limit: int, progress=None) -> List[Dict]:
    """
    Scrape jobs from Glassdoor using the role name.
    """
    from .glassdoor_selenium import scrape_glassdoor_jobs
    
    print(f"Scraping Glassdoor for '{role_name}' jobs")
    
    if progress:
        progress.update("glassdoor", 20, 100, f"Scraping Glassdoor for '{role_name}'...")
    
    # Call the Selenium-based Glassdoor scraper
    jobs = scrape_glassdoor_jobs(role_name, limit, progress=progress)
    
    if progress:
        progress.update("glassdoor", 60, 100, f"Found {len(jobs)} jobs from Glassdoor")
    
    # Convert to the expected format
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "title": job.get("job_title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("job_description", "N/A"),
            "source_url": job.get("source_url", ""),
            "sources": ["glassdoor"]
        })
    
    print(f"Converted to {len(formatted_jobs)} formatted jobs")
    return formatted_jobs


def scrape_glassdoor_from_url(filtered_url: str, limit: int) -> List[Dict]:
    """
    Scrape jobs from Glassdoor using the provided filtered URL.
    """
    from .glassdoor_requests import scrape_glassdoor
    
    print("Using requests-based Glassdoor scraper")
    
    # Extract keyword and location from URL or use defaults
    keyword = "software engineer"  # Default keyword
    location = "United States"     # Default location
    
    print(f"Searching for '{keyword}' jobs in '{location}'")
    
    # Call the requests-based glassdoor scraper
    jobs = scrape_glassdoor(keyword, location, num_pages=1, max_jobs=limit)
    print(f"Glassdoor scraper returned {len(jobs)} jobs")
    
    # Convert to the expected format
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "title": job.get("job_title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("job_description", "N/A"),
            "source_url": job.get("source_url", ""),
            "sources": ["glassdoor"]
        })
    
    print(f"Converted to {len(formatted_jobs)} formatted jobs")
    return formatted_jobs


def scrape_indeed_from_role(role_name: str, location: str, limit: int, progress=None) -> List[Dict]:
    """
    Scrape jobs from Indeed using the role name and location.
    """
    from .indeed_scraper import scrape_indeed_jobs
    
    print(f"Scraping Indeed for '{role_name}' jobs in '{location}'")
    
    if progress:
        progress.update("indeed", 20, 100, f"Scraping Indeed for '{role_name}' in '{location}'...")
    
    # Call the Indeed scraper
    jobs = scrape_indeed_jobs(role_name, limit, location, progress=progress)
    print(f"Indeed scraper returned {len(jobs)} jobs")
    
    if progress:
        progress.update("indeed", 60, 100, f"Found {len(jobs)} jobs from Indeed")
    
    # Convert to the expected format
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "title": job.get("job_title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("job_description", "N/A"),
            "source_url": job.get("source_url", ""),
            "sources": ["indeed"]
        })
    
    print(f"Converted to {len(formatted_jobs)} formatted jobs")
    return formatted_jobs


def scrape_indeed_from_url(filtered_url: str, limit: int) -> List[Dict]:
    """
    Scrape jobs from Indeed using the provided filtered URL.
    """
    from .indeed_scraper import scrape_indeed
    
    print("Using Indeed scraper")
    
    # Extract keyword and location from URL or use defaults
    keyword = "software engineer"  # Default keyword
    location = "United States"     # Default location
    
    print(f"Searching Indeed for '{keyword}' jobs in '{location}'")
    
    # Call the Indeed scraper
    jobs = scrape_indeed(keyword, location, max_jobs=limit)
    print(f"Indeed scraper returned {len(jobs)} jobs")
    
    # Convert to the expected format
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "title": job.get("job_title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("job_description", "N/A"),
            "source_url": job.get("source_url", ""),
            "sources": ["indeed"]
        })
    
    print(f"Converted to {len(formatted_jobs)} formatted jobs")
    return formatted_jobs


def scrape_advanced_from_url(filtered_url: str, limit: int, progress=None) -> List[Dict]:
    """
    Advanced scraper that tries multiple job sites.
    """
    from .advanced_scraper import scrape_jobs_advanced
    
    print("Using advanced multi-site scraper")
    
    # Extract keyword and location from URL or use defaults
    keyword = "software engineer"  # Default keyword
    location = "United States"     # Default location
    
    print(f"Searching multiple sites for '{keyword}' jobs in '{location}'")
    print(f"Target: {limit} jobs")
    
    # Call the advanced scraper
    jobs = scrape_jobs_advanced(keyword, location, max_jobs=limit)
    print(f"Advanced scraper returned {len(jobs)} jobs")
    
    # Convert to the expected format
    formatted_jobs = []
    for i, job in enumerate(jobs, 1):
        formatted_job = {
            "title": job.get("job_title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "description": job.get("job_description", "N/A"),
            "source_url": job.get("source_url", ""),
            "sources": ["multi-site"]
        }
        formatted_jobs.append(formatted_job)
        print(f"Processed job {i}/{len(jobs)}: {formatted_job['title']} at {formatted_job['company']}")
    
    print(f"Converted to {len(formatted_jobs)} formatted jobs")
    return formatted_jobs


def scrape_linkedin_from_url(filtered_url: str, limit: int) -> List[Dict]:
    """
    Placeholder for LinkedIn scraping - to be implemented
    """
    # TODO: Implement LinkedIn scraping
    return []


@transaction.atomic
def save_jobs_to_database(jobs: List[Dict], platform: str) -> int:
    """
    Save scraped jobs to the database with deduplication.
    """
    print(f"Attempting to save {len(jobs)} jobs to database")
    added_count = 0
    
    for i, job_data in enumerate(jobs):
        try:
            print(f"Processing job {i+1}: {job_data.get('title', 'N/A')} at {job_data.get('company', 'N/A')}")
            
            # Create fingerprint for deduplication
            fp = fingerprint(job_data["title"], job_data["company"], job_data["location"])
            print(f"Fingerprint: {fp}")
            
            # Get or create company
            company, created = Company.objects.get_or_create(
                name=job_data["company"],
                defaults={"website": None, "email": None}
            )
            print(f"Company: {company.name} (created: {created})")
            
            # Check if job already exists
            existing_job = Job.objects.filter(fingerprint=fp, company=company).first()
            
            if existing_job:
                print(f"Job already exists, updating sources")
                # Update sources if not already present
                if platform not in existing_job.sources:
                    existing_job.sources.append(platform)
                    existing_job.save()
            else:
                print(f"Creating new job")
                # Create new job
                Job.objects.create(
                    title=job_data["title"],
                    location=job_data["location"],
                    company=company,
                    description=job_data["description"],
                    source_url=job_data["source_url"],
                    sources=[platform],
                    fingerprint=fp
                )
                added_count += 1
                print(f"Job created successfully")
                
        except Exception as e:
            print(f"Error saving job {i+1}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"Successfully saved {added_count} new jobs")
    return added_count
