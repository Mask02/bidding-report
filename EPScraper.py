from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from FileManager import write_data_into_json, create_output_dir
from selenium.webdriver.chrome.options import Options


class EPScraper:

    def __init__(self):

        self.EP_BASE_URL = "https://www.eastplainscorporation.com/foreclosure-listings"

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")  # Make browser headless

        self.driver = webdriver.Chrome(options=options)  # Initializing Microsoft's Edge Webdriver

        self.data = list()

        self.data_keys = ["Sale_date", "Sale_time", "FileNo", "PropAddress", "PropCity", "OpeningBid"]

        self.output_directory_name = "EP-Scraper-Output"

        create_output_dir(self.output_directory_name)

    def scrape(self):

        self.driver.get(self.EP_BASE_URL)

        time.sleep(5)

        iframe_src = self.driver.find_element(By.CLASS_NAME, 'wuksD5').get_attribute('src')

        self.driver.get(iframe_src)

        time.sleep(5)

        table_rows = list(self.driver.find_elements(By.TAG_NAME, 'tr'))[1:]

        for row in table_rows:

            row_dict = {
                "Trustee": "",
                "Sale_date": "",
                "Sale_time": "",
                "County": "",
                "FileNo": "",
                "PropAddress": "",
                "PropCity": "",
                "PropZip": "",
                "OpeningBid": ""
            }

            row_dict["Trustee"] = "EastPlains"

            cols = list(row.find_elements(By.TAG_NAME, 'td'))[:-1]

            cols.pop(len(cols) - 2)  # Remove state column

            for c_index in range(len(cols)):
                row_dict[self.data_keys[c_index]] = cols[c_index].text

            if len(row_dict["FileNo"]) != 0:
                self.data.append(row_dict)

        write_data_into_json("output/" + self.output_directory_name + "/ep_data", self.data)

        return "output/" + self.output_directory_name + "/ep_data.xlsx"
