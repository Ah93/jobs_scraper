import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def _scroll(driver, times=4, pause=1.2):
    """Scroll the page to load more content."""
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)


def parse_indeed(driver, filtered_url: str, limit: int) -> List[Dict]:
    """Parse Indeed job listings from a filtered URL."""
    driver.get(filtered_url)
    time.sleep(2)
    _scroll(driver, times=6)
    
    cards = driver.find_elements(By.CSS_SELECTOR, "a[data-jk], a.tapItem")[:limit]
    results = []
    
    for card in cards:
        try:
            href = card.get_attribute("href")
            title = card.find_element(By.CSS_SELECTOR, "h2 span").text
            company = card.find_element(By.CSS_SELECTOR, "span.companyName").text
            location = card.find_element(By.CSS_SELECTOR, "div.companyLocation").text
            
            # Open detail to scrape description
            driver.execute_script("window.open(arguments[0], '_blank');", href)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(1.5)
            
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            desc_el = soup.select_one("#jobDescriptionText")
            desc = desc_el.get_text("\n", strip=True) if desc_el else ""
            
            results.append({
                "title": title,
                "company": company,
                "location": location,
                "description": desc,
                "source_url": href,
                "platform": "indeed",
            })
        except Exception:
            pass
        finally:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            if len(results) >= limit:
                break
                
    return results


def parse_glassdoor(driver, filtered_url: str, limit: int) -> List[Dict]:
    """Parse Glassdoor job listings from a filtered URL."""
    driver.get(filtered_url)
    time.sleep(3)
    _scroll(driver, times=6)
    
    cards = driver.find_elements(By.CSS_SELECTOR, "a[data-test='job-link']")[:limit]
    results = []
    
    for card in cards:
        try:
            href = card.get_attribute("href")
            title = card.find_element(By.CSS_SELECTOR, "h3[data-test='job-title']").text
            company = card.find_element(By.CSS_SELECTOR, "[data-test='employer-name']").text
            location = card.find_element(By.CSS_SELECTOR, "[data-test='job-location']").text
            
            # Click to get full description
            driver.execute_script("arguments[0].click();", card)
            time.sleep(2)
            
            # Close any popup modals
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, ".modal_closeIcon")
                close_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Extract description
            try:
                description = driver.find_element(By.CSS_SELECTOR, "[data-test='jobDescriptionText']").text
            except:
                description = ""
            
            results.append({
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "source_url": href,
                "platform": "glassdoor",
            })
            
        except Exception as e:
            print(f"Error parsing Glassdoor job: {e}")
            continue
            
    return results


def parse_linkedin(driver, filtered_url: str, limit: int) -> List[Dict]:
    """Parse LinkedIn job listings from a filtered URL."""
    # TODO: Implement LinkedIn parsing
    return []