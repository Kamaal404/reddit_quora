#!/usr/bin/env python
"""
Manual Quora Login Script - Simplified for Windows

This script provides a very simplified approach to log into Quora
without using WebDriverManager, which seems to cause issues on your system.
"""

import os
import sys
import time
import yaml
import logging
from pathlib import Path

# Configure simple logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("manual_quora_login")

# Define paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CREDENTIALS_PATH = PROJECT_ROOT / "config" / "credentials.yml"

def load_credentials():
    """Load Quora credentials from config file."""
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            credentials = yaml.safe_load(f)
        
        quora_creds = credentials.get("quora", {})
        username = quora_creds.get("username")
        password = quora_creds.get("password")
        
        if not username or not password:
            logger.error("Missing Quora credentials")
            return None, None
            
        logger.info(f"Loaded credentials for: {username}")
        return username, password
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return None, None

def manual_quora_login():
    """Very simple Quora login approach."""
    username, password = load_credentials()
    if not username or not password:
        logger.error("Cannot proceed without credentials")
        return
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
    except ImportError:
        logger.error("Selenium not installed. Please run: pip install selenium")
        return
    
    # Set up Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    
    # Launch Chrome directly, without using WebDriverManager
    logger.info("Launching Chrome browser")
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome launched successfully")
    except Exception as e:
        logger.error(f"Failed to launch Chrome: {e}")
        logger.info("Please make sure Chrome is installed properly")
        return
    
    # Navigate to Quora login page
    logger.info("Going to Quora login page")
    driver.get("https://www.quora.com/login")
    time.sleep(5)
    
    # Log page info
    logger.info(f"Current URL: {driver.current_url}")
    
    # Take screenshot
    screenshot_path = os.path.join(PROJECT_ROOT, "logs", "login_page.png")
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    driver.save_screenshot(screenshot_path)
    logger.info(f"Screenshot saved to {screenshot_path}")
    
    # Print input fields and buttons found
    inputs = driver.find_elements(By.TAG_NAME, "input")
    logger.info(f"Found {len(inputs)} input fields")
    
    buttons = driver.find_elements(By.TAG_NAME, "button")
    logger.info(f"Found {len(buttons)} buttons")
    
    # Try method 1: Accessing inputs by index
    logger.info("Trying login method 1: By input index")
    try:
        if len(inputs) >= 2:
            # First input should be email
            email_input = inputs[0]
            email_input.clear()
            email_input.send_keys(username)
            logger.info("Entered email")
            
            # Second input should be password
            password_input = inputs[1]
            password_input.clear()
            password_input.send_keys(password)
            logger.info("Entered password")
            
            # Try to find login button
            if buttons:
                buttons[0].click()
                logger.info("Clicked first button")
            else:
                # Or submit by pressing Enter
                password_input.send_keys(Keys.RETURN)
                logger.info("Pressed Enter to submit")
                
            # Wait for login
            time.sleep(7)
            
            # Check if login successful
            if "login" not in driver.current_url:
                logger.info("Login successful!")
            else:
                logger.warning("Login seems to have failed")
        else:
            logger.warning("Not enough input fields found")
    except Exception as e:
        logger.error(f"Error in login attempt: {e}")
    
    # Wait for user to see the result
    try:
        input("Press Enter to close the browser...")
    except:
        pass
    
    # Clean up
    driver.quit()

if __name__ == "__main__":
    logger.info("Starting manual Quora login script")
    manual_quora_login()
    logger.info("Script completed") 