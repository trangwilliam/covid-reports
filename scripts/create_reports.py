import os, datetime, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

    # Create webdriver
    covid_dash_link = os.getenv("COVID_DASH_LINK")
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
    except:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.get(covid_dash_link)

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
        driver (Selenium.WebDriver): WebDriver for COVID PowerBI Dashboard, logged in 
    """

    # Create the webdriver
    driver = setup_covid_bi()
    wait = WebDriverWait(driver, 10)

    # Open the dashboard and log in with credentials
    try:
        email_input = wait.until(EC.presence_of_element_located((By.NAME, 'loginfmt')))
        email_input.clear()
        email_input.send_keys(user)

        next_btn = wait.until(EC.presence_of_element_located((By.ID, 'idSIButton9')))
        next_btn.click()
    except:
        teardown(driver)
    
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

    # Open the dashboard in fullscreen
    try:
        view_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="app-bar-view-menu-btn"]')))
        view_btn.click()

        fullscreen_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="open-in-full-screen-btn"]')))
        fullscreen_btn.click()
    except:
        teardown(driver)
    
    # Wait for the report to fullscreen
    time.sleep(5)
    img_filepaths = ['screenshots/' + date_short + '_0' + str(i) + '.png' for i in range(1, 4)]

    # Take screenshots of the first 3 pages of the dashboard
    try:
        next_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="fullscreen-navigate-next-btn"]')))
        driver.save_screenshot(img_filepaths[0])

        next_btn.click()
        time.sleep(3)
        driver.save_screenshot(img_filepaths[1])

        next_btn.click()
        time.sleep(3)
        driver.save_screenshot(img_filepaths[2])
    except:
        teardown(driver)

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
    driver = powerbi_login(user) 
    image_filepaths = screenshot_bi(driver)
    save_reports(image_filepaths)