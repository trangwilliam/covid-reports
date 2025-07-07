import os, datetime, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from PIL import Image

# Dates for report naming
curr_date = datetime.datetime.now()
date_formatted = curr_date.strftime('%m.%d.%Y')
date_short = curr_date.strftime('%m%d%y')

def setup_covid_bi():
    """
    Creates a Chrome WebDriver for COVID Power BI Dashboard

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

    # Create webdriver
    covid_dash_link = os.getenv("COVID_DASH_LINK")
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
    except:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.get(covid_dash_link) # type: ignore
    print(f"Navigated to: {driver.current_url}")
    print(driver.find_element(By.XPATH, "/html/body").text)

    return driver

def teardown(driver) -> None:
    """
    Closes all browser windows and ends session for input WebDriver

    Args:
        driver (Selenium.WebDriver): WebDriver for COVID PowerBI Dashboard 
    """
    
    driver.quit()

def powerbi_login(user: str):
    """
    Logs in to Microsoft Account to access COVID PowerBI Dashboard
    
    Args:
        user (String): Username of login account
    Returns:
        driver (Selenium.WebDriver): WebDriver for COVID Power BI Dashboard, logged in 
    """

    # Create the webdriver
    driver = setup_covid_bi()
    wait = WebDriverWait(driver, 30)  # Increased timeout for CI environment

    # Open the dashboard and log in with credentials
    try:
        print("Waiting for login form...")
        email_input = wait.until(EC.presence_of_element_located((By.NAME, 'loginfmt')))
        email_input.clear()
        email_input.send_keys(user)
        print(f"Entered email: {user}")

        next_btn = wait.until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
        next_btn.click()
        print("Clicked next button")
        
        # Wait for password field to appear
        password_input = wait.until(EC.presence_of_element_located((By.NAME, 'passwd')))
        password = os.getenv("METRO_PASSWORD")
        
        password_input.clear()
        password_input.send_keys(password)  # type: ignore
        print("Entered password")
        
        # Click sign in button
        signin_btn = wait.until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
        signin_btn.click()
        print("Clicked sign in button")
        
        # Handle "Stay signed in?" dialog if it appears
        try:
            stay_signed_in = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'idSIButton9'))
            )
            stay_signed_in.click()
            print("Clicked 'Stay signed in' button")
        except TimeoutException:
            print("No 'Stay signed in' dialog found, continuing...")
            
    except TimeoutException as e:
        print(f'Login timeout error: {e}')
        print(f'Current page source: {driver.page_source[:500]}...')
        teardown(driver)
        raise
    except Exception as e:
        print(f'Login error: {e}')
        print(f'Current page source: {driver.page_source[:500]}...')
        teardown(driver)
        raise
    
    print('Post login successful')
    print(f'Current URL: {driver.current_url}')
    print(driver.find_element(By.XPATH, "/html/body").text)
    
    return driver

def screenshot_bi(driver) -> list:
    """
    Takes screenshots of first three pages of COVID PowerBI Dashboard, and saves them to a filepath
    
    Args:
        driver (Selenium.WebDriver): WebDriver for COVID PowerBI Dashboard, logged in 
    Returns:
        img_filepaths (list): List of filepaths for COVID dashboard screenshots 
    """

    # Get the webdriver and create the output directory
    wait = WebDriverWait(driver, 20)
    output_dir = 'screenshots'
    os.makedirs(output_dir, exist_ok=True)

    try:
        os.makedirs(output_dir, exist_ok=True)
        # Test write permissions
        test_file = os.path.join(output_dir, 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✓ Directory created and writable: {os.path.abspath(output_dir)}")
    except Exception as e:
        print(f"✗ Directory creation/write test failed: {e}")
        # Fallback to current directory
        output_dir = '.'
        print(f"Using current directory: {os.path.abspath(output_dir)}")

    try:
        current_url = driver.current_url
        print(f"Driver status OK. Current URL: {current_url}")
    except Exception as e:
        print(f"✗ Driver appears to be dead: {e}")

    try:
        fullscreen_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="open-in-full-screen-btn"]')))
        print("✓ Fullscreen button found")
    except TimeoutException:
        print("✗ Fullscreen button not found within timeout period")
    except Exception as e:
        print(f"✗ Error checking for fullscreen button: {e}")

    # Open the dashboard in fullscreen
    try:
        print("Looking for view menu button...")
        view_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="app-bar-view-menu-btn"]')))
        view_btn.click()
        print("Clicked view menu button")

        print("Looking for fullscreen button...")
        fullscreen_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="open-in-full-screen-btn"]')))
        fullscreen_btn.click()
        print("Clicked fullscreen button")
    except TimeoutException as e:
        print(f"Timeout waiting for fullscreen elements: {e}")
        print("Attempting to take screenshots without fullscreen...")
    except Exception as e:
        print(f"Error opening fullscreen: {e}")
        print("Attempting to take screenshots without fullscreen...")
    
    # Wait for the report to fullscreen
    time.sleep(5)
    img_filepaths = ['screenshots/' + date_short + '_0' + str(i) + '.png' for i in range(1, 4)]

    # Take screenshots of the first 3 pages of the dashboard
    try:
        print("Looking for navigation buttons...")
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@data-testid="fullscreen-navigate-next-btn"]')))
        print("Taking screenshot of page 1...")
        driver.save_screenshot(img_filepaths[0])
        print(f"Saved screenshot to: {img_filepaths[0]}")

        print("Navigating to page 2...")
        next_btn.click()
        time.sleep(5)  # Increased wait time for CI
        print("Taking screenshot of page 2...")
        driver.save_screenshot(img_filepaths[1])
        print(f"Saved screenshot to: {img_filepaths[1]}")

        print("Navigating to page 3...")
        next_btn.click()
        time.sleep(5)  # Increased wait time for CI
        print("Taking screenshot of page 3...")
        driver.save_screenshot(img_filepaths[2])
        print(f"Saved screenshot to: {img_filepaths[2]}")
    except TimeoutException as e:
        print(f"Timeout waiting for navigation elements: {e}")
        print("Taking single screenshot of current page...")
        driver.save_screenshot(img_filepaths[0])
    except Exception as e:
        print(f"Error taking screenshots: {e}")
        print("Taking single screenshot of current page...")
        driver.save_screenshot(img_filepaths[0])

    teardown(driver)
    return img_filepaths

def save_reports(img_filepaths: list) -> None:
    """
    Takes dashboard screenshots and converts them into pre-outlined report formats
    
    Args:
        img_filepaths (list): List of filepaths for COVID dashboard screenshots
    """

    print(os.listdir('screenshots'))

    # Declare the output filepaths
    output_dir = 'reports'
    union_data_report_fp = os.path.join(output_dir, f'Union Data Report ({date_formatted}).pdf')
    daily_covid_report_fp = os.path.join(output_dir, f'Daily COVID Report ({date_formatted}).pdf')

    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save the union data report
    union_report = Image.open(img_filepaths[0])
    union_report.convert('RGB').save(union_data_report_fp)

    # Save the daily COVID report
    daily_report = union_report.save(
        daily_covid_report_fp, 'PDF', resolution=100, save_all=True, append_images=[Image.open(fp) for fp in img_filepaths[1:]]
    )

def create_all_reports() -> None:
    """
    Creates and saves all daily reports relating to COVID-19
    """

    user = os.getenv("METRO_EMAIL")
    driver = powerbi_login(user)  # type: ignore 
    image_filepaths = screenshot_bi(driver)
    save_reports(image_filepaths)