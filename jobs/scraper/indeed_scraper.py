import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random, urllib.parse
from .driver import build_driver


def scrape_indeed_jobs(job_title, num_jobs=50, location="New York, NY", progress=None):
    """
    Scrape jobs from Indeed until num_jobs is reached.
    
    job_title : str -> job keyword, e.g. "Data Scientist"
    num_jobs  : int -> number of jobs to scrape in total
    location  : str -> location string
    progress  : ProgressTracker object for progress updates
    """

    # Encode the query for URL - try different formats
    job_encoded = urllib.parse.quote_plus(job_title)
    location_encoded = urllib.parse.quote_plus(location)
    
    # Try different URL formats
    url_formats = [
        f"https://www.indeed.com/jobs?q={job_encoded}&l={location_encoded}",
        f"https://www.indeed.com/jobs?q={job_encoded}&l={location_encoded}&sort=date",
        f"https://www.indeed.com/jobs?q={job_encoded}&l={location_encoded}&fromage=7",
        f"https://www.indeed.com/jobs?q={job_encoded}&l={location_encoded}&sort=relevance"
    ]
    
    base_url = url_formats[0]  # Start with the first format

    # Setup WebDriver with anti-detection measures
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Create custom options for better anti-detection
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1366,768")
        # Try headless first, but have fallback
        chrome_options.add_argument("--headless=new")
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Randomize window size slightly
        import random
        width = 1366 + random.randint(-100, 100)
        height = 768 + random.randint(-100, 100)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Chrome driver initialized successfully for Indeed with anti-detection")
    except Exception as e:
        print(f"Error initializing Chrome driver for Indeed: {e}")
        return []

    # Storage lists
    titles, companies, locations, descriptions, urls = [], [], [], [], []

    def scrape_current_page():
        """Scrape all jobs on the current page"""
        try:
            # Try multiple selectors for job cards
            job_selectors = [
                "div[data-testid='slider_item']",
                "div.job_seen_beacon",
                "div[data-testid='job-card']",
                "div.jobsearch-SerpJobCard",
                "div[data-jk]",
                "div[data-testid='job-listing']",
                "div[class*='job']",
                "div[class*='Job']"
            ]
            
            job_cards = []
            for selector in job_selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        print(f"Found {len(job_cards)} job cards with selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards:
                print("⚠️ No job cards found with any selector")
                # Debug: Print page source snippet to see what's available
                print("Page title:", driver.title)
                print("Current URL:", driver.current_url)
                # Try to find any div elements that might contain jobs
                all_divs = driver.find_elements(By.TAG_NAME, "div")
                print(f"Found {len(all_divs)} div elements on page")
                # Look for any elements with 'job' in class name
                job_like_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'Job')]")
                print(f"Found {len(job_like_divs)} divs with 'job' in class name")
                
                # Try a more generic approach - look for any clickable elements that might be job titles
                try:
                    generic_jobs = driver.find_elements(By.XPATH, "//a[contains(@href, '/viewjob') or contains(@href, '/jobs')]")
                    print(f"Found {len(generic_jobs)} generic job links")
                    if generic_jobs:
                        print("Trying generic approach...")
                        # Use the generic jobs as job cards
                        job_cards = generic_jobs
                    else:
                        return
                except Exception as e:
                    print(f"Generic approach failed: {e}")
                    return

        except Exception as e:
            print("⚠️ Failed to load job listings:", e)
            return

        for card in job_cards:
            if len(titles) >= num_jobs:  # Stop once we reach target
                return

            try:
                # Title - try multiple selectors
                title_selectors = [
                    "a[data-testid='job-title']",
                    "h2[data-testid='job-title']",
                    "h2.jobTitle a",
                    "h2.jobTitle",
                    "a[data-testid='slider_item'] h2",
                    "a[data-testid='job-title'] span",
                    "h2 a span",
                    "a[data-testid='job-title'] h2",
                    "a[data-testid='job-title'] h3",
                    "span",  # For generic approach
                    "h2",
                    "h3"
                ]
                
                title_text = "N/A"
                for selector in title_selectors:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, selector)
                        title_text = title_elem.text.strip()
                        if title_text:
                            break
                    except:
                        continue
                
                # Fallback: if no specific selector worked, try to get any text from the card
                if title_text == "N/A":
                    try:
                        card_text = card.text.strip()
                        if card_text and len(card_text) > 10:  # Make sure it's not just whitespace
                            # Take the first line as title
                            title_text = card_text.split('\n')[0][:100]  # Limit length
                    except:
                        pass
                
                titles.append(title_text)

                # Company - try multiple selectors
                company_selectors = [
                    "span[data-testid='company-name']",
                    "div[data-testid='company-name']",
                    "span.companyName",
                    "div.companyName"
                ]
                
                company_text = "N/A"
                for selector in company_selectors:
                    try:
                        company_elem = card.find_element(By.CSS_SELECTOR, selector)
                        company_text = company_elem.text.strip()
                        if company_text:
                            break
                    except:
                        continue
                companies.append(company_text)

                # Location - try multiple selectors
                location_selectors = [
                    "div[data-testid='text-location']",
                    "div[data-testid='job-location']",
                    "div.location",
                    "span.location"
                ]
                
                location_text = "N/A"
                for selector in location_selectors:
                    try:
                        location_elem = card.find_element(By.CSS_SELECTOR, selector)
                        location_text = location_elem.text.strip()
                        if location_text:
                            break
                    except:
                        continue
                locations.append(location_text)

                # Description - try to get job summary
                desc_selectors = [
                    "div[data-testid='job-snippet']",
                    "div.job-snippet",
                    "div.summary",
                    "ul"
                ]
                
                desc_text = "N/A"
                for selector in desc_selectors:
                    try:
                        desc_elem = card.find_element(By.CSS_SELECTOR, selector)
                        desc_text = desc_elem.text.strip()
                        if desc_text:
                            break
                    except:
                        continue
                descriptions.append(desc_text)

                # Job Link - try multiple selectors
                link_selectors = [
                    "a.jcs-JobTitle",
                    "a[data-testid='job-title']",
                    "h2.jobTitle a"
                ]
                
                link_url = "N/A"
                for selector in link_selectors:
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, selector)
                        href = link_elem.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                link_url = "https://www.indeed.com" + href
                            else:
                                link_url = href
                            break
                    except:
                        continue
                
                # Fallback: if the card itself is a link, use its href
                if link_url == "N/A":
                    try:
                        if card.tag_name == "a":
                            href = card.get_attribute("href")
                            if href:
                                if href.startswith("/"):
                                    link_url = "https://www.indeed.com" + href
                                else:
                                    link_url = href
                    except:
                        pass
                
                urls.append(link_url)
                
            except Exception as e:
                print(f"Error processing job card: {e}")
                # Add N/A values if there's an error
                titles.append("N/A")
                companies.append("N/A")
                locations.append("N/A")
                descriptions.append("N/A")
                urls.append("N/A")

    try:
        # Try different URLs if blocked
        success = False
        for i, url in enumerate(url_formats):
            print(f"Trying URL format {i+1}: {url}")
            
            # Add random delay before navigation
            time.sleep(random.uniform(2, 4))
            
            driver.get(url)
            print(f"Page loaded. Title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            
            # Wait a bit for page to fully load with random delay
            time.sleep(random.uniform(3, 6))
            
            # Check if we got redirected or blocked
            if "captcha" in driver.current_url.lower() or "blocked" in driver.current_url.lower() or "blocked" in driver.title.lower():
                print(f"⚠️ URL {i+1} appears to be blocked")
                if i < len(url_formats) - 1:
                    print("Trying next URL format...")
                    continue
                else:
                    print("All URL formats blocked. Indeed may be detecting automation.")
                    return []
            else:
                print(f"✅ URL {i+1} loaded successfully!")
                success = True
                break
        
        if not success:
            print("All headless URL attempts failed. Trying non-headless mode...")
            
            # Try without headless mode as last resort
            try:
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1366,768")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Close headless driver and create new non-headless one
                driver.quit()
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                print("Trying with visible browser...")
                driver.get(url_formats[0])
                time.sleep(5)
                
                if "blocked" in driver.title.lower():
                    print("Still blocked even with visible browser.")
                    driver.quit()
                    return []
                else:
                    print("✅ Visible browser worked!")
                    success = True
                    
            except Exception as e:
                print(f"Non-headless attempt also failed: {e}")
                return []
        
        if not success:
            print("All attempts failed.")
            return []
        
        page = 1

        while len(titles) < num_jobs:
            print(f"🔎 Scraping Indeed page {page}...")
            if progress:
                progress.update("indeed", 20 + (len(titles) / num_jobs) * 60, 100, f"Scraping Indeed page {page}... Found {len(titles)} jobs")
            
            # Human-like scrolling before scraping
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
            time.sleep(random.uniform(1, 2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            
            scrape_current_page()

            if len(titles) >= num_jobs:
                break

            # Try clicking next with human-like behavior
            try:
                next_button = None
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")
                except:
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
                    except:
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")
                        except:
                            next_button = None

                if not next_button:
                    print("🚫 No more pages available.")
                    break

                # Scroll to the next button
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(random.uniform(1, 2))
                
                # Click with human-like delay
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(random.uniform(4, 8))  # mimic human browsing
                page += 1

            except Exception as e:
                print("🚫 Pagination ended:", e)
                break

        # Convert to the expected format
        jobs = []
        for i in range(len(titles)):
            jobs.append({
                "job_title": titles[i],
                "company_name": companies[i],
                "location": locations[i],
                "job_description": descriptions[i],
                "source_url": urls[i]
            })

        print(f"✅ Indeed scraping completed. Found {len(jobs)} jobs")
        return jobs

    except Exception as e:
        print(f"Error during Indeed scraping: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        try:
            driver.quit()
        except:
            pass


def scrape_indeed(job_title, location="New York, NY", max_jobs=50):
    """
    Legacy function for compatibility with existing pipeline
    """
    return scrape_indeed_jobs(job_title, max_jobs, location)