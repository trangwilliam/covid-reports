#!/usr/bin/env python3
"""
Test script to debug environment variables and Chrome setup in GitHub Actions
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("=== Testing Environment Variables ===")
    
    required_vars = [
        'COVID_DASH_LINK',
        'METRO_EMAIL', 
        'METRO_PASSWORD',
        'REPORT_SITE_NAME',
        'DAILY_REPORT_EXT',
        'UNION_REPORT_EXT', 
        'WEEKEND_REPORT_EXT',
        'SHAREPOINT_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (length: {len(value)})")
        else:
            print(f"✗ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All environment variables are set")
        return True

def test_chrome_setup():
    """Test Chrome WebDriver setup"""
    print("\n=== Testing Chrome Setup ===")
    
    try:
        # Set up Chrome options similar to create_reports.py
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        print("✓ Chrome options configured")
        
        # Try to create WebDriver
        try:
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            print("✓ Chrome WebDriver created with default service")
        except Exception as e:
            print(f"⚠ Default service failed: {e}")
            print("Trying with ChromeDriverManager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✓ Chrome WebDriver created with ChromeDriverManager")
        
        # Test navigation
        test_url = "https://www.google.com"
        print(f"Testing navigation to: {test_url}")
        driver.get(test_url)
        
        title = driver.title
        print(f"✓ Successfully loaded page with title: '{title}'")
        
        # Test screenshot
        screenshot_path = "test_screenshot.png"
        driver.save_screenshot(screenshot_path)
        if os.path.exists(screenshot_path):
            print(f"✓ Screenshot saved to: {screenshot_path}")
            os.remove(screenshot_path)  # Clean up
        else:
            print("✗ Screenshot failed")
        
        driver.quit()
        print("✓ Chrome WebDriver test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Chrome setup failed: {e}")
        return False

def test_powerbi_access():
    """Test access to Power BI dashboard"""
    print("\n=== Testing Power BI Access ===")
    
    covid_dash_link = os.getenv("COVID_DASH_LINK")
    if not covid_dash_link:
        print("✗ COVID_DASH_LINK not set, skipping Power BI test")
        return False
    
    try:
        # Set up Chrome options
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Create WebDriver
        try:
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
        except:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        
        print(f"Navigating to Power BI dashboard...")
        driver.get(covid_dash_link)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Check if we're on a login page
        page_source = driver.page_source.lower()
        if "sign in" in page_source or "login" in page_source or "microsoft" in page_source:
            print("✓ Successfully reached Power BI login page")
        else:
            print("⚠ Page content doesn't appear to be a login page")
            print(f"Page source preview: {driver.page_source[:500]}...")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"✗ Power BI access test failed: {e}")
        return False

if __name__ == "__main__":
    print("GitHub Actions Environment Test")
    print("=" * 40)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test Chrome setup
    chrome_ok = test_chrome_setup()
    
    # Test Power BI access
    powerbi_ok = test_powerbi_access()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print(f"Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"Chrome Setup: {'✅' if chrome_ok else '❌'}")
    print(f"Power BI Access: {'✅' if powerbi_ok else '❌'}")
    
    if all([env_ok, chrome_ok, powerbi_ok]):
        print("\n🎉 All tests passed! Your environment should work with the main scripts.")
        sys.exit(0)
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
        sys.exit(1) 