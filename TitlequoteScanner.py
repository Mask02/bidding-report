from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from FileManager import create_output_dir 
from selenium.webdriver.chrome.options import Options


class TitlequoteScanner:
    def __init__(self):
        self.EP_BASE_URL = "https://titlequote.stlmsd.com/#/"
        self.output_directory_name = "TitlequoteScanner-Output"
        self.json_file_path = f"output/{self.output_directory_name}/tq_data.json"
        if os.path.exists(self.json_file_path):
            try:
                os.remove(self.json_file_path)
                print(f"Deleted existing file: {self.json_file_path}")
            except OSError as e:
                print(f"Error deleting file: {e}")
        
        # Initialize Chrome options
        options = Options()
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless")  # Uncomment for headless mode

        # Use Chrome WebDriver (you can switch to Edge if preferred)
        self.driver = webdriver.Chrome(options=options)
        
        # List to store all scraped data in memory
        self.data = []
        
        # Create output directory
        create_output_dir(self.output_directory_name)

    def scrape(self):
        self.driver.maximize_window()
        self.driver.get(self.EP_BASE_URL)

        self.login()
        self.change_no_of_results()

        # Scrape all pages
        while True:
            self.get_data()
            number_of_pages_div = self.driver.find_element(By.CLASS_NAME, "mat-mdc-paginator-range-label")
            total_results = int(number_of_pages_div.text.split(' ')[-1])
            current_results = int(number_of_pages_div.text.split(' ')[-3])
            print(f"Current: {current_results}, Total: {total_results}")
            if current_results < total_results:
                self.next_page()
            else:
                break

        self.append_to_json()

        self.driver.quit()
        return self.json_file_path

    def login(self):
        USERNAME = "cary@caryandcompany.com"
        PASSWORD = "Bocce2025"
        time.sleep(30)  # Adjust this if manual login isn’t needed
        
        login_input = self.driver.find_element(By.ID, "username")
        login_input.send_keys(USERNAME)
        
        password_input = self.driver.find_element(By.ID, "password")
        password_input.send_keys(PASSWORD)
        time.sleep(10)

        login_button = self.driver.find_elements(By.CLASS_NAME, "ng-touched")[0].find_element(By.TAG_NAME, "button")
        login_button.click()
        print("Logged In")
        time.sleep(20)

    def change_no_of_results(self):
        time.sleep(5)
        change_pages = self.driver.find_element(By.ID, "mat-select-0")
        if change_pages:
            change_pages.click()
            time.sleep(10)
            
            options_div = self.driver.find_element(By.ID, "mat-select-0-panel")
            options = options_div.find_elements(By.TAG_NAME, "mat-option")
            if options:
                options[-1].click()  
            time.sleep(15)

    def get_data(self):
        
        headers = [
            "Seller Name", "Service Address", "Zip Code", "Locator", "Quote ID",
            "Quote Amount", "Closing Date", "Stage", "Submitted By"
        ]
        column_classes = [
            "cdk-column-sellerLastName", "cdk-column-propertyAddrLine1", "cdk-column-propertyZip",
            "cdk-column-locatorNumber", "cdk-column-id", "cdk-column-balanceDue",
            "cdk-column-dealClosingDate", "cdk-column-queueName", "cdk-column-user"
        ]
        
        # Scrape table rows
        tbody = self.driver.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            row_data = {}
            cells = row.find_elements(By.TAG_NAME, "td")
            for header, cell in zip(headers, cells):
                # Clean seller name by removing button text if present
                text = cell.text.strip()
                if header == "Seller Name" and "PendingCloseReached" in cell.get_attribute("innerHTML"):
                    text = text.split("\xa0", 1)[-1]  # Remove button prefix (non-breaking space)
                row_data[header] = text
            self.data.append(row_data)
        
        print(f"Scraped {len(rows)} rows from this page")

    def next_page(self):
        button = self.driver.find_element(By.CLASS_NAME, "mat-mdc-paginator-navigation-next")
        if button:
            button.click()
            time.sleep(10)

    def append_to_json(self):
        # Load existing data from JSON file if it exists
        existing_data = []
        if os.path.exists(self.json_file_path):
            try:
                with open(self.json_file_path, "r") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                print("Existing JSON file is corrupt; starting fresh.")
        
        # Append new data, avoiding duplicates based on Quote ID
        existing_quote_ids = {item["Quote ID"] for item in existing_data}
        for new_item in self.data:
            if new_item["Quote ID"] not in existing_quote_ids:
                existing_data.append(new_item)
                existing_quote_ids.add(new_item["Quote ID"])
        
        # Write combined data back to JSON
        with open(self.json_file_path, "w") as f:
            json.dump(existing_data, f, indent=4)
        print(f"Appended data to {self.json_file_path}, total records: {len(existing_data)}")


if __name__ == "__main__":
    scanner = TitlequoteScanner()
    scanner.scrape()