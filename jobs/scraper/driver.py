import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # pip install webdriver-manager




def build_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1366,768")
    # Optional: random user agent / proxy from env
    ua = os.getenv("SCRAPER_USER_AGENT")
    if ua:
        opts.add_argument(f"--user-agent={ua}")
    proxy = os.getenv("SCRAPER_HTTP_PROXY")
    if proxy:
        opts.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    return driver