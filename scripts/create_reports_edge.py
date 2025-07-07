import os, datetime, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from PIL import Image

# Dates for report naming
curr_date = datetime.datetime.now()
date_formatted = curr_date.strftime('%m.%d.%Y')
date_short = curr_date.strftime('%m%d%y')

def setup_covid_bi():
    """
    Creates an Edge WebDriver for COVID Power BI Dashboard
    Edge sometimes handles Windows Integrated Auth better than Chrome

    Returns:
        driver (Selenium.WebDriver): WebDriver for COVID PowerBI Dashboard 
    """

    # Set options for WebDriver
    scale_factor = 0.2
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f"--force-device-scale-factor={scale_factor}")
    options.add_argument('--log-level=1')
    
    # Additional options for GitHub Actions/CI environment
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Edge-specific authentication options
    options.add_argument('--auth-server-whitelist="*"')
    options.add_argument('--auth-negotiate-delegate-whitelist="*"')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Edge-specific options for Windows auth
    options.add_argument('--enable-features=msImeMenu')
    options.add_argument('--disable-features=TranslateUI')

    # Create webdriver
    covid_dash_link = os.getenv("COVID_DASH_LINK")
    
    try:
        service = Service()
        driver = webdriver.Edge(service=service, options=options)
    except:
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

    driver.get(covid_dash_link) # type: ignore
    print(f"Navigated to: {driver.current_url}")
    print(driver.find_element(By.XPATH, "/html/body").text)

    return driver

# ... rest of the functions would be the same as create_reports.py ... 