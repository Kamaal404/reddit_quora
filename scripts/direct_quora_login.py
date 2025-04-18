#!/usr/bin/env python
"""
Direct Quora Login Script

This script provides a focused, direct approach to logging into Quora
using exact browser automation. It will try multiple methods to find 
and interact with the login form elements.
"""

import os
import sys
import time
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{log_dir}/direct_quora_login.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("direct_quora_login")

# Define the paths relative to the script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CREDENTIALS_PATH = PROJECT_ROOT / "config" / "credentials.yml"
LOGS_PATH = PROJECT_ROOT / "logs"

def save_screenshot(driver, name):
    """Save a screenshot with a timestamp in the filename."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = LOGS_PATH / f"{name}_{timestamp}.png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        driver.save_screenshot(str(filename))
        logger.info(f"Screenshot saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")

def save_page_source(driver, name):
    """Save the page source with a timestamp in the filename."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = LOGS_PATH / f"{name}_{timestamp}.html"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Page source saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save page source: {e}")

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

def quora_login():
    """
    Main function to perform the Quora login.
    Tries multiple different approaches to handle Quora's changing login form.
    """
    try:
        # Load the credentials
        username, password = load_credentials()
        if not username or not password:
            logger.error("Cannot proceed without valid credentials")
            return False
            
        # Import Selenium components
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            logger.error("Please install Selenium: pip install selenium")
            return False
            
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Maximize the browser window
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Try to hide automation
        
        # Add user-agent to appear more like a real browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Launch the browser - try different approaches
        logger.info("Launching Chrome browser")
        
        try:
            # Try approach 1: Use the default Chrome installation
            logger.info("Trying to launch Chrome (approach 1)")
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome launched successfully with approach 1")
        except Exception as e1:
            logger.warning(f"Failed to launch Chrome with approach 1: {e1}")
            
            try:
                # Try approach 2: Use the Chrome service with explicit path
                import os
                from selenium.webdriver.chrome.service import Service
                
                # Try to find Chrome in common locations
                chrome_locations = [
                    "C:/Program Files/Google/Chrome/Application/chrome.exe",
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
                ]
                
                chrome_path = None
                for location in chrome_locations:
                    if os.path.exists(location):
                        chrome_path = location
                        break
                
                if chrome_path:
                    logger.info(f"Found Chrome at: {chrome_path}")
                    chrome_options.binary_location = chrome_path
                
                # Try providing a service without WebDriverManager
                logger.info("Trying to launch Chrome (approach 2)")
                driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome launched successfully with approach 2")
            except Exception as e2:
                logger.warning(f"Failed to launch Chrome with approach 2: {e2}")
                
                try:
                    # Try approach 3: Use Selenium Manager
                    logger.info("Trying to launch Chrome (approach 3)")
                    driver = webdriver.Chrome(options=chrome_options)
                    logger.info("Chrome launched successfully with approach 3")
                except Exception as e3:
                    logger.error(f"All Chrome launch methods failed. Last error: {e3}")
                    logger.error("Please make sure Chrome is installed properly")
                    
                    # Check if undetected-chromedriver is available as a last resort
                    try:
                        import undetected_chromedriver as uc
                        logger.info("Trying with undetected-chromedriver as last resort")
                        driver = uc.Chrome()
                        logger.info("Chrome launched with undetected-chromedriver")
                    except ImportError:
                        logger.error("undetected-chromedriver not available")
                        return False
                    except Exception as e4:
                        logger.error(f"Failed to launch Chrome with undetected-chromedriver: {e4}")
                        return False
        
        # Set a longer timeout for page loads
        driver.set_page_load_timeout(30)
        
        # Apply additional anti-detection measures
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
        except Exception as e:
            logger.warning(f"Failed to apply anti-detection measures: {e}")
        
        # Go to the Quora login page
        logger.info("Navigating to Quora login page")
        driver.get("https://www.quora.com/login")
        
        # Wait for the page to load
        time.sleep(5)
        
        # Save initial state
        save_screenshot(driver, "login_page")
        save_page_source(driver, "login_page_source")
        
        # Check the current URL to see if we're on the login page
        logger.info(f"Current URL: {driver.current_url}")
        
        # Get all available input elements on the page to analyze the form structure
        inputs = driver.find_elements(By.TAG_NAME, "input")
        logger.info(f"Found {len(inputs)} input elements on the page")
        
        # Log all input fields for analysis
        for i, input_field in enumerate(inputs):
            try:
                field_type = input_field.get_attribute("type")
                field_name = input_field.get_attribute("name")
                field_id = input_field.get_attribute("id")
                field_class = input_field.get_attribute("class")
                logger.info(f"Input field #{i+1}: type={field_type}, name={field_name}, id={field_id}, class={field_class}")
            except:
                logger.info(f"Input field #{i+1}: [Error getting attributes]")
        
        # Get all buttons on the page
        buttons = driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"Found {len(buttons)} button elements on the page")
        
        # Log all buttons for analysis
        for i, button in enumerate(buttons):
            try:
                button_text = button.text
                button_class = button.get_attribute("class")
                logger.info(f"Button #{i+1}: text='{button_text}', class={button_class}")
            except:
                logger.info(f"Button #{i+1}: [Error getting attributes]")
        
        # APPROACH 1: Try using the known XPath selectors
        logger.info("APPROACH 1: Using provided XPath selectors")
        try:
            # Find email input field
            email_xpath = "/html/body/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[2]/input"
            email_field = driver.find_element(By.XPATH, email_xpath)
            
            # Clear and enter email
            email_field.clear()
            logger.info(f"Entering username: {username}")
            email_field.send_keys(username)
            time.sleep(1)
            save_screenshot(driver, "after_email_input")
            
            # Find password input field
            password_xpath = "/html/body/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[3]/div[2]/input"
            password_field = driver.find_element(By.XPATH, password_xpath)
            
            # Clear and enter password
            password_field.clear()
            logger.info("Entering password")
            password_field.send_keys(password)
            time.sleep(1)
            save_screenshot(driver, "after_password_input")
            
            # Find and click login button
            login_button_xpath = "/html/body/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[4]/button"
            login_button = driver.find_element(By.XPATH, login_button_xpath)
            logger.info("Clicking login button")
            login_button.click()
            logger.info("Login button clicked")
            
            # Wait for login to complete
            time.sleep(7)
            save_screenshot(driver, "after_login_attempt")
            
            # Check if login was successful
            if "login" not in driver.current_url:
                logger.info("Login successful!")
                save_screenshot(driver, "login_success")
                input("Press Enter to close the browser...")
                driver.quit()
                return True
            else:
                logger.warning("Login attempt with XPath selectors failed")
        except NoSuchElementException as e:
            logger.warning(f"XPath approach failed: {e}")
        except Exception as e:
            logger.warning(f"Error in XPath approach: {e}")
        
        # APPROACH 2: Try using general attribute selectors
        logger.info("APPROACH 2: Using attribute selectors")
        try:
            # Refresh the page to get a clean login form
            driver.refresh()
            time.sleep(5)
            save_screenshot(driver, "page_refreshed")
            
            # Find the email field by looking for an email type input
            email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            email_input.clear()
            logger.info(f"Entering username: {username}")
            email_input.send_keys(username)
            time.sleep(1)
            save_screenshot(driver, "after_email_input_css")
            
            # Find the password field by looking for a password type input
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            logger.info("Entering password")
            password_input.send_keys(password)
            time.sleep(1)
            save_screenshot(driver, "after_password_input_css")
            
            # Find the login button
            # First try to find it by looking for text content
            try:
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log') or contains(text(), 'Sign') or contains(text(), 'log') or contains(text(), 'sign')]")
            except NoSuchElementException:
                # If that fails, try to find the form and get the button from there
                form = driver.find_element(By.TAG_NAME, "form")
                login_button = form.find_element(By.TAG_NAME, "button")
            
            logger.info("Clicking login button")
            login_button.click()
            logger.info("Login button clicked")
            
            # Wait for login to complete
            time.sleep(7)
            save_screenshot(driver, "after_login_attempt_css")
            
            # Check if login was successful
            if "login" not in driver.current_url:
                logger.info("Login successful!")
                save_screenshot(driver, "login_success_css")
                input("Press Enter to close the browser...")
                driver.quit()
                return True
            else:
                logger.warning("Login attempt with CSS selectors failed")
        except NoSuchElementException as e:
            logger.warning(f"CSS approach failed: {e}")
        except Exception as e:
            logger.warning(f"Error in CSS approach: {e}")
        
        # APPROACH 3: Try focusing on the inputs directly by their index
        logger.info("APPROACH 3: Using input index approach")
        try:
            # Refresh the page again
            driver.refresh()
            time.sleep(5)
            save_screenshot(driver, "page_refreshed_again")
            
            # Get all inputs on the page
            inputs = driver.find_elements(By.TAG_NAME, "input")
            if len(inputs) >= 2:  # We expect at least 2 inputs: email and password
                # Assume first input is email
                email_input = inputs[0]
                email_input.clear()
                logger.info(f"Entering username: {username}")
                email_input.send_keys(username)
                time.sleep(1)
                
                # Assume second input is password
                password_input = inputs[1]
                password_input.clear()
                logger.info("Entering password")
                password_input.send_keys(password)
                time.sleep(1)
                save_screenshot(driver, "after_index_inputs")
                
                # Try to find the submit button - either it's a button after the inputs,
                # or we can submit the form by pressing Enter
                try:
                    # Look for any button that might be the submit button
                    submit_button = None
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    if buttons:
                        # Try to find the most likely login button
                        for button in buttons:
                            if button.is_displayed() and button.is_enabled():
                                button_text = button.text.lower()
                                if any(keyword in button_text for keyword in ["log", "sign", "submit", "enter"]):
                                    submit_button = button
                                    break
                        
                        # If we couldn't find a specific login button, use the first available button
                        if not submit_button and buttons:
                            submit_button = buttons[0]
                            
                        if submit_button:
                            logger.info("Clicking submit button")
                            submit_button.click()
                    else:
                        # If no buttons found, try pressing Enter on the password field
                        logger.info("No buttons found, pressing Enter on password field")
                        password_input.send_keys(Keys.RETURN)
                except Exception as button_error:
                    logger.warning(f"Error finding/clicking button: {button_error}")
                    # Try pressing Enter as fallback
                    logger.info("Pressing Enter on password field as fallback")
                    password_input.send_keys(Keys.RETURN)
                
                # Wait for login to complete
                time.sleep(7)
                save_screenshot(driver, "after_index_login")
                
                # Check if login was successful
                if "login" not in driver.current_url:
                    logger.info("Login successful!")
                    save_screenshot(driver, "login_success_index")
                    input("Press Enter to close the browser...")
                    driver.quit()
                    return True
                else:
                    logger.warning("Login attempt with index approach failed")
            else:
                logger.warning(f"Not enough inputs found: {len(inputs)}")
        except NoSuchElementException as e:
            logger.warning(f"Index approach failed: {e}")
        except Exception as e:
            logger.warning(f"Error in index approach: {e}")
        
        # APPROACH 4: Try using JavaScript to directly set input values
        logger.info("APPROACH 4: Using JavaScript direct access")
        try:
            # Refresh the page again
            driver.refresh()
            time.sleep(5)
            save_screenshot(driver, "page_refreshed_for_js")
            
            # Use JavaScript to fill form fields and submit
            js_script = f"""
            // Find all input elements
            var inputs = document.getElementsByTagName('input');
            var emailInput = null;
            var passwordInput = null;
            
            // Identify email and password fields
            for (var i = 0; i < inputs.length; i++) {{
                var input = inputs[i];
                var type = input.getAttribute('type');
                
                if (type === 'email' || input.getAttribute('placeholder')?.toLowerCase().includes('email')) {{
                    emailInput = input;
                }} else if (type === 'password') {{
                    passwordInput = input;
                }}
            }}
            
            // Fill the fields if found
            if (emailInput) {{
                emailInput.value = "{username}";
                console.log("Email field filled");
            }}
            
            if (passwordInput) {{
                passwordInput.value = "{password}";
                console.log("Password field filled");
            }}
            
            // Find submit button
            var buttons = document.getElementsByTagName('button');
            var submitButton = null;
            
            // Look for a likely submit button
            for (var i = 0; i < buttons.length; i++) {{
                var button = buttons[i];
                var text = button.textContent.toLowerCase();
                if (text.includes('log') || text.includes('sign') || button.getAttribute('type') === 'submit') {{
                    submitButton = button;
                    break;
                }}
            }}
            
            // Click the submit button if found
            if (submitButton) {{
                submitButton.click();
                console.log("Submit button clicked");
                return true;
            }} else if (passwordInput) {{
                // If no submit button found, try to submit the form containing the password field
                var form = passwordInput.closest('form');
                if (form) {{
                    form.submit();
                    console.log("Form submitted");
                    return true;
                }}
            }}
            
            return false;
            """
            
            result = driver.execute_script(js_script)
            logger.info(f"JavaScript execution result: {result}")
            
            # Wait for login to complete
            time.sleep(7)
            save_screenshot(driver, "after_js_login")
            
            # Check if login was successful
            if "login" not in driver.current_url:
                logger.info("Login successful with JavaScript approach!")
                save_screenshot(driver, "login_success_js")
                input("Press Enter to close the browser...")
                driver.quit()
                return True
            else:
                logger.warning("Login attempt with JavaScript failed")
        except Exception as e:
            logger.warning(f"Error in JavaScript approach: {e}")
        
        # If we've reached here, all approaches failed
        logger.error("All login approaches failed")
        
        # Take final screenshot
        save_screenshot(driver, "all_approaches_failed")
        
        # Let the user see the final state before closing
        input("All login approaches failed. Press Enter to close the browser...")
        driver.quit()
        return False
        
    except Exception as e:
        logger.exception(f"Unexpected error in login process: {e}")
        return False

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs(LOGS_PATH, exist_ok=True)
    
    logger.info("Starting direct Quora login script")
    success = quora_login()
    
    if success:
        logger.info("Login process completed successfully")
    else:
        logger.error("Login process failed") 