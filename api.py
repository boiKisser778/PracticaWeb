from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile

# Configure Chrome options for headless operation
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Headless mode (no UI)
chrome_options.add_argument('--no-sandbox')  # Disable sandbox for Docker
chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome shared memory issues in Docker

# Optional: use a unique user-data-dir for each session to avoid conflicts
chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')

# Set up ChromeDriver
service = Service(ChromeDriverManager().install())

def UwUnify(message):
    # Initialize the WebDriver with the options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://orientallines.github.io/uwufy/"

    try:
        # Open the URL
        driver.get(url)

        # Wait for the text input field to be clickable
        text_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'textInput'))
        )

        # Wait for the UwUinate button to be clickable
        uwuinate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@onclick='uwuinate();']"))
        )

        # Input the message text into the text area
        text_input.send_keys(message)

        # Click the UwUinate button
        uwuinate_button.click()

        # Wait for the result output to be present
        result_output = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'textResult'))
        )

        # Retrieve the UwUified text
        result_text = result_output.get_attribute('value')

        return result_text

    except Exception as e:
        # If something goes wrong, print the error
        print(f"An error occurred: {e}")
        return None

    finally:
        # Ensure that the WebDriver quits properly
        driver.quit()

# Example usage:
if __name__ == "__main__":
    message = "Hello, how are you?"
    uwuified_text = UwUnify(message)
    print(uwuified_text)
