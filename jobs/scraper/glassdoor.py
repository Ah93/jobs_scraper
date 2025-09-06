import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
from webdriver_manager.chrome import ChromeDriverManager

def scrape_glassdoor(keyword: str, location: str, num_pages: int = 1, max_jobs: int = 50):
    print(f"Starting Glassdoor scrape for '{keyword}' in '{location}'")
    
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Add user agent to look more like a real browser
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Enable headless mode for production
    options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        print("Chrome driver initialized successfully")
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        return []

    try:
        # Navigate to Glassdoor
        driver.get("https://www.glassdoor.com/Job/index.htm")
        print("Navigated to Glassdoor")
        time.sleep(5)

        # Wait for page to load and look for search elements
        try:
            # Try to find search input with multiple selectors
            search_selectors = [
                "input[id='KeywordSearch']",
                "input[placeholder*='Job title']",
                "input[placeholder*='keyword']",
                "input[data-test='keyword-input']"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found search input with selector: {selector}")
                    break
                except:
                    continue
            
            if not search_input:
                print("Could not find search input, trying alternative approach")
                print("Page title:", driver.title)
                print("Current URL:", driver.current_url)
                return []

            # Find location input
            location_selectors = [
                "input[id='LocationSearch']",
                "input[placeholder*='Location']",
                "input[data-test='location-input']"
            ]
            
            location_input = None
            for selector in location_selectors:
                try:
                    location_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found location input with selector: {selector}")
                    break
                except:
                    continue

            if search_input and location_input:
                # Clear and fill inputs
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(1)
                
                location_input.clear()
                location_input.send_keys(location)
                time.sleep(1)
                
                # Find and click search button
                search_button_selectors = [
                    "button[id='HeroSearchButton']",
                    "button[data-test='search-button']",
                    "button[type='submit']",
                    "input[type='submit']"
                ]
                
                search_button = None
                for selector in search_button_selectors:
                    try:
                        search_button = driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"Found search button with selector: {selector}")
                        break
                    except:
                        continue
                
                if search_button:
                    search_button.click()
                    print("Search submitted")
                    time.sleep(8)  # Wait for results to load
                else:
                    print("Could not find search button")
                    return []
            else:
                print("Could not find required input fields")
                return []

        except Exception as e:
            print(f"Error with search form: {e}")
            return []

        # Look for job listings
        jobs = []
        
        # Multiple selectors for job cards
        job_selectors = [
            "li[data-adv-type='GENERAL']",
            "div[data-test='job-listing']",
            "article[data-test='job-card']",
            "div.jobContainer",
            "div[class*='job']",
            "li[class*='job']"
        ]
        
        job_cards = []
        for selector in job_selectors:
            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"Found {len(job_cards)} job cards with selector: {selector}")
                    break
            except:
                continue
        
        if not job_cards:
            print("No job cards found with any selector")
            print("Page title:", driver.title)
            print("Current URL:", driver.current_url)
            return []

        # Process job cards
        for idx, card in enumerate(job_cards[:max_jobs]):
            try:
                print(f"Processing job {idx + 1}")
                
                # Scroll to the card
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(1)
                
                # Try to click the card
                try:
                    driver.execute_script("arguments[0].click();", card)
                    time.sleep(3)
                except:
                    try:
                        card.click()
                        time.sleep(3)
                    except:
                        print(f"Could not click job card {idx + 1}")
                        continue

                # Close any popup modals
                try:
                    close_buttons = driver.find_elements(By.CSS_SELECTOR, ".modal_closeIcon, .close, [aria-label='Close']")
                    for btn in close_buttons:
                        if btn.is_displayed():
                            btn.click()
                            time.sleep(1)
                            break
                except:
                    pass

                # Extract job information
                job = {
                    "company_name": "N/A",
                    "job_title": "N/A", 
                    "location": "N/A",
                    "job_description": "N/A",
                    "salary": "N/A",
                    "source_url": driver.current_url,
                }

                # Try multiple selectors for company name
                company_selectors = [
                    "div[data-test='employer-name']",
                    "span[data-test='employer-name']",
                    "div[class*='companyName']",
                    "span[class*='companyName']",
                    "h3[class*='company']",
                    "div[class*='company']"
                ]
                
                for selector in company_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            job["company_name"] = element.text.strip()
                            break
                    except:
                        continue

                # Try multiple selectors for job title
                title_selectors = [
                    "h2[data-test='job-title']",
                    "div[data-test='job-title']",
                    "h2[class*='jobTitle']",
                    "div[class*='jobTitle']",
                    "a[class*='jobTitle']",
                    "h3[class*='job']"
                ]
                
                for selector in title_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            job["job_title"] = element.text.strip()
                            break
                    except:
                        continue

                # Try multiple selectors for location
                location_selectors = [
                    "div[data-test='job-location']",
                    "span[data-test='job-location']",
                    "div[class*='location']",
                    "span[class*='location']"
                ]
                
                for selector in location_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            job["location"] = element.text.strip()
                            break
                    except:
                        continue

                # Try to get job description
                desc_selectors = [
                    "div[id='JobDescriptionContainer']",
                    "div[data-test='job-description']",
                    "div[class*='description']"
                ]
                
                for selector in desc_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.text.strip():
                            job["job_description"] = element.text.strip()
                            break
                    except:
                        continue

                # Only add if we got meaningful data
                if job["job_title"] != "N/A" or job["company_name"] != "N/A":
                    jobs.append(job)
                    print(f"Added job: {job['job_title']} at {job['company_name']}")
                else:
                    print(f"Job {idx + 1} had insufficient data")

                if len(jobs) >= max_jobs:
                    break

            except Exception as e:
                print(f"Error scraping job card {idx + 1}: {e}")
                continue

        print(f"Scraping completed. Found {len(jobs)} jobs")
        return jobs

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        try:
            driver.quit()
        except:
            pass
