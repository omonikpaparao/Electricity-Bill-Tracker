import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Automatically install the correct version of chromedriver
chromedriver_autoinstaller.install()

# Set up Chrome options
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

# URL of the APCPDCL service details page
url = "https://apcpdcl.in/ConsumerDashboard/serviceDetails.jsp"

# Example service number
service_number = "1122500406058"  # Replace with your actual service number

# Data to store extracted details
data = []

try:
    # Open the URL
    driver.get(url)

    # Wait until the service number input field is visible
    service_number_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.NAME, "service_number"))
    )

    # Enter the service number
    service_number_input.send_keys(service_number)

    # Wait until the submit button is visible and click it
    submit_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
    )
    submit_button.click()

    # Wait for the service details to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "details"))
    )

    # Extract and store data (modify according to the actual page structure)
    service_details = driver.find_elements(By.CLASS_NAME, "details")
    
    # If service details are found
    if service_details:
        for detail in service_details:
            detail_text = detail.text.strip()

            # Search for a specific keyword to identify bill details (e.g., "Bill" or "Amount")
            if "Bill" in detail_text or "Amount" in detail_text:
                bill_amount = detail_text
                data.append([service_number, bill_amount])  # Store service number and bill amount
            else:
                data.append([service_number, "Bill not found"])

    else:
        print("No details found for the given service number.")
    
except Exception as e:
    print(f"Error: {e}")

finally:
    # Check if we have data to save
    if data:
        # Convert data into a DataFrame and write it to an Excel file
        df = pd.DataFrame(data, columns=["Service Number", "Bill Amount"])

        # Write to Excel file
        df.to_excel("electric_bill_details.xlsx", index=False)
        print("Data successfully saved to electric_bill_details.xlsx")
    else:
        print("No data extracted.")

    # Close the browser
    driver.quit()
