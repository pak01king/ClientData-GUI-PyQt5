import sys
import datetime
import sqlite3
import threading
import time
import requests
import logging
from flask import Flask
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures

API_KEY = '3a5fd13d15749c24a5e58c6d0d1e90bd'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


def solve_recaptcha(site_key, url):
    data = {
        'clientKey': API_KEY,
        'task': {
            'type': 'NoCaptchaTaskProxyless',
            'websiteURL': url,
            'websiteKey': site_key
        }
    }

    response = requests.post('https://api.anti-captcha.com/createTask', json=data)
    if response.status_code == 200:
        task_id = response.json().get('taskId')
        if task_id:
            # Wait for the task to be solved
            while True:
                response = requests.post('https://api.anti-captcha.com/getTaskResult', json={'clientKey': API_KEY, 'taskId': task_id})
                if response.status_code == 200:
                    result = response.json().get('solution')
                    if result and result.get('gRecaptchaResponse'):
                        return result['gRecaptchaResponse']
                # Wait for a few seconds before checking the task status again
                time.sleep(2)

    return None 


def process_client(first_name, last_name, idnp, email, chromedriver_path):
    driver = None 
    try:
        # Set up the Selenium WebDriver with incognito mode
        options = Options()

        user_agent = UserAgent().random
        # Set custom user agent
        options.add_argument(f"--user-agent={user_agent}")

        # Launch the WebDriver in incognito mode
        options.add_argument("--incognito")

        # Launch the WebDriver with the provided chromedriver_path
        service = Service(chromedriver_path)
        service.start()
        driver = webdriver.Chrome(service=service, options=options)

        # Open the website
        driver.get('http://programari.starecivila1.ro/')

        # Stage 1: Fill the input fields and submit the form
        first_name_input = WebDriverWait(driver, 3600).until(EC.presence_of_element_located((By.ID, 'first_name')))
        first_name_input.send_keys(first_name)

        last_name_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'last_name')))
        last_name_input.send_keys(last_name)

        idnp_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'idnp')))
        idnp_input.send_keys(idnp)

        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        email_input.send_keys(email)

        checkbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'md-checkbox-1-input')))
        checkbox.click()

        # Solve recaptcha
        recaptcha_checkbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'recaptcha-checkbox-border')))
        recaptcha_checkbox.click()

        site_key = '3a5fd13d15749c24a5e58c6d0d1e90bd'  # Enter the reCAPTCHA site key for the website
        url = driver.current_url
        g_recaptcha_response = solve_recaptcha(site_key, url)

        if g_recaptcha_response:
            driver.execute_script(f"document.getElementById('g-recaptcha-response').value = '{g_recaptcha_response}';")

        submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'submit_button')))
        submit_button.click()

        # Stage 2: Wait for the date options to load
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-option')))

        # Stage 3: Select an available date
        date_dropdown = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-select-trigger')))
        date_dropdown.click()

        date_options = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-option')))

        # Dynamic wait until an available date is found
        for date_option in date_options:
            if 'mat-option-disabled' not in date_option.get_attribute('class'):
                date_option.click()

                programeaza_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button/span[contains(text(), 'Programează')]")))
                programeaza_button.click()

                break

        logging.info(f"Client processed: {first_name} {last_name}")

    except TimeoutException:
        logging.error("Timeout occurred while waiting for an element.")
        # Handle timeout exception here

    except NoSuchElementException:
        logging.error("Element not found on the page.")
        # Handle element not found exception here

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        if driver is not None:
            driver.quit()
            service.stop()


def automate_data_entry(chromedriver_path):
    current_date = datetime.datetime.now().day
    if current_date != 15:
        return

    # Connect to the database
    conn = sqlite3.connect('database/ClientAdd.db')
    c = conn.cursor()

    # Retrieve data from the database
    c.execute("SELECT first_name, last_name, idnp, email FROM Clients WHERE status = 'PENDING'")
    records = c.fetchall()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a thread for each record and start the registration process
        futures = [executor.submit(process_client, *record, chromedriver_path) for record in records]

        # Wait for all threads to complete
        concurrent.futures.wait(futures)
        
    # Create a thread for each record and start the registration process
    threads = []
    for record in records:
        first_name, last_name, idnp, email = record
        thread = threading.Thread(target=process_client, args=(first_name, last_name, idnp, email, chromedriver_path))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Close the database connection
    conn.close()


app = Flask(__name__)

@app.route('/automate', methods=['GET'])
def automate_api():
    threading.Thread(target=automate_data_entry, args=(app.config['CHROMEDRIVER_PATH'],)).start()
    return 'Data entry automation initiated'


if __name__ == '__main__':
    # Check if the chromedriver path is provided as a command-line argument
    if len(sys.argv) > 1:
        chromedriver_path = sys.argv[1]
    else:
        chromedriver_path = 'drivers/chromedriver'  # Replace with the default path to chromedriver

    # Set the chromedriver path as a configuration variable
    app.config['CHROMEDRIVER_PATH'] = chromedriver_path

    # Run the Flask app
    app.run()
