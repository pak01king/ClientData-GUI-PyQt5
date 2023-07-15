import sys
from datetime import date, timedelta
import sqlite3
import threading
import time
import requests
import logging
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright
from playwright.sync_api import Error as PlaywrightError

API_KEY = 'c07364d922ddd0f97613e88facb2cd3e'

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')


def solve_recaptcha(site_key, url):
    data = {
        'key': API_KEY,
        'method': 'userrecaptcha',
        'googlekey': site_key,
        'pageurl': url,
        'json': 1
    }

    response = requests.post('http://2captcha.com/in.php', data=data)
    if response.status_code == 200:
        captcha_id = response.json().get('request')
        if captcha_id:
            # Wait for the captcha to be solved
            while True:
                response = requests.get(f'http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1')
                if response.status_code == 200:
                    result = response.json().get('request')
                    if result == 'CAPCHA_NOT_READY':
                        # Wait for a few seconds before checking the captcha status again
                        time.sleep(5)
                    elif 'OK' in result:
                        return result['OK']

    return None


def process_client(last_name, first_name, idnp, email, chromedriver_path):
    playwright, browser, context = setup_playwright(chromedriver_path)

    try:
        # Open the website
        page = context.new_page()
        page.goto('http://programari.starecivila1.ro/')

        while True:
            try:
                refresh_button = page.wait_for_selector('.mat-button-wrapper')
                refresh_button.click()
                break
            except PlaywrightError.TimeoutError:
                time.sleep(2)

        num_repeats = 1000
        for _ in range(num_repeats):
            # Wait until the "Refresh" button is visible
            refresh_button = page.wait_for_selector('.mat-button-wrapper')

            # Click the "Refresh" button
            refresh_button.click()

        # Stage 1: Fill the input fields and submit the form
        last_name_input = page.wait_for_selector('#last_name')
        last_name_input.fill(last_name)

        first_name_input = page.wait_for_selector('#first_name')
        first_name_input.fill(first_name)

        idnp_input = page.wait_for_selector('#idnp')
        idnp_input.fill(idnp)

        email_input = page.wait_for_selector('#email')
        email_input.fill(email)

        checkbox = page.wait_for_selector('#md-checkbox-1-input')
        checkbox.click()

        # Solve reCAPTCHA
        recaptcha_checkbox = page.wait_for_selector('.recaptcha-checkbox-border')
        recaptcha_checkbox.click()

        site_key = '6Lc6s1kcAAAAAJFZF7bEztSBUEDeBU_0jl4qUtWA'  # Enter the reCAPTCHA site key for the website
        url = page.url
        g_recaptcha_response = solve_recaptcha(site_key, url)

        if g_recaptcha_response:
            page.evaluate(f"document.getElementById('g-recaptcha-response').value = '{g_recaptcha_response}';")
        else:
            manual_input = input("Please manually solve the reCAPTCHA and enter the response: ")
            page.evaluate(f"document.getElementById('g-recaptcha-response').value = '{manual_input}';")

        submit_button = page.wait_for_selector('#submit_button')
        submit_button.click()

        # Stage 2: Wait for the date options to load
        page.wait_for_selector('.mat-option')

        # Stage 3: Select an available date
        date_dropdown = page.wait_for_selector('.mat-select-trigger')
        date_dropdown.click()

        date_options = page.wait_for_selector_all('.mat-option')

        # Dynamic wait until an available date is found
        for date_option in date_options:
            if 'mat-option-disabled' not in date_option.get_attribute('class'):
                date_option.click()

                programeaza_button = page.wait_for_selector("//button/span[contains(text(), 'Programează')]")
                programeaza_button.click()

                break

        logging.info(f"Client processed: {first_name} {last_name}")

    except PlaywrightError.TimeoutError:
        logging.error("Timeout occurred while waiting for an element.")
        # Handle timeout exception here

    except PlaywrightError.ElementHandleError:
        logging.error("Element not found on the page.")
        # Handle element not found exception here

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        close_playwright(playwright, browser)


def setup_playwright(chromedriver_path):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    return playwright, browser, context


def close_playwright(playwright, browser):
    browser.close()
    playwright.stop()


def automate_data_entry(chromedriver_path):
    current_date = date.today()

    # Check if the current date is a weekend or the 15th day of the month
    if current_date.weekday() >= 5 or current_date.day == 12:
        # Add one day to the current date to get the next working day
        current_date += timedelta(days=1)

    # Connect to the database
    conn = sqlite3.connect('database/ClientAdd.db')
    c = conn.cursor()

    # Retrieve data from the database
    c.execute("SELECT first_name, last_name, idnp, email FROM Clients WHERE status = 'PENDING'")
    records = c.fetchall()

    for record in records:
        process_client(*record, chromedriver_path)

    # Update the status of the processed clients
    c.execute("UPDATE Clients SET status = 'PROCESSED' WHERE status = 'PENDING'")
    conn.commit()

    # Close the database connection
    conn.close()


if __name__ == '__main__':
    # Check if the chromedriver path is provided as a command-line argument
    if len(sys.argv) > 1:
        chromedriver_path = sys.argv[1]
    elif sys.platform == 'darwin':  # Check if it's macOS
        chromedriver_path = 'drivers/chromedriver_mac'  # Replace with the actual path to chromedriver on macOS
    else:
        chromedriver_path = 'drivers/chromedriver'  # Replace with the actual path to chromedriver on other platforms

    automate_data_entry(chromedriver_path)
