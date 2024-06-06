from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from FileManager import write_data_into_json, create_output_dir
from selenium.webdriver.chrome.options import Options
import os


class TitlequoteScanner:

    def __init__(self):

        self.EP_BASE_URL = "https://titlequote.stlmsd.com/#/"

        options = Options()
        # options.add_argument('--proxy-server=%s' % proxy_url)
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")  # Make browser headless

        self.driver = webdriver.Chrome(options=options)  # Initializing Microsoft's Edge Webdriver

        self.data = list()

        self.output_directory_name = "TitlequoteScanner-Output"

        create_output_dir(self.output_directory_name)

    def scrape(self):

        self.driver.maximize_window()
        self.driver.get(self.EP_BASE_URL)
        USERNAME_ = "cary@caryandcompany.com"
        PASSWORD = "Tornado1963"
        time.sleep(30)
        login_input = self.driver.find_element(By.ID, "username")

        if login_input:
            login_input.send_keys(USERNAME_)

        password_input = self.driver.find_element(By.ID, "password")

        if password_input:
            password_input.send_keys(PASSWORD)
        time.sleep(10)

        login_button = self.driver.find_element(By.XPATH,
                                                "/html/body/div/div[2]/div/div/div[2]/div/div/div/div[7]/form/div[4]/div/button")

        if login_button:
            login_button.click()

        print("Logged In")
        time.sleep(20)
        self.page_scrape()

    def page_scrape(self):
        self.get_data()
        number_of_pages_div = self.driver.find_element(By.XPATH,
                                                       "/html/body/div/div[2]/div/div/md-content/md-tabs/md-tabs-content-wrapper/md-tab-content[1]/div/md-content/form/div/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/input")
        number_of_pages = int(number_of_pages_div.get_attribute("max"))
        print(number_of_pages)
        if number_of_pages > 1:
            button = self.driver.find_element(By.XPATH,
                                              "/html/body/div/div[2]/div/div/md-content/md-tabs/md-tabs-content-wrapper/md-tab-content[1]/div/md-content/form/div/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/button[3]")
            if button:
                button.click()
                time.sleep(10)
                self.get_data()

    def get_data(self):

        change_pages = self.driver.find_element(By.XPATH,
                                                '//*[@id="tab-content-0"]/div/md-content/form/div/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[2]/select')
        if change_pages:
            change_pages.click()
            time.sleep(5)
            options = change_pages.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                last_options = options[-1]
                last_options.click()
            time.sleep(15)

            # Seller Name

        seller_name_list = []
        seller_names = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-006")

        for seller in seller_names:
            seller_name_list.append(seller.text)
        print("seller_name_list", seller_name_list)

        # Seller Address

        service_address_list = []
        service_address = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-007")

        for address in service_address:
            service_address_list.append(address.text)
        print("service_address_list", service_address_list)

        # Zip codes

        zip_code_list = []
        zip_codes = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-008")

        for zip_code in zip_codes:
            zip_code_list.append(zip_code.text)
        print("zip_code_list", zip_code_list)

        # locators
        locators_list = []
        locators = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-009")
        for locator in locators:
            locators_list.append(locator.text)
        print("locators_list", locators_list)

        # Quotes ID
        quote_ids_list = []
        quote_ids = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-00A")

        for quote_id in quote_ids:
            # print(quote_id.text)
            quote_ids_list.append(quote_id.text)
        print("quote_ids_list", quote_ids_list)

        # Quote Amounts

        quote_amounts_list = []
        quote_amounts = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-00B")

        for quote_amount in quote_amounts:
            # print(quote_amount.text)
            quote_amounts_list.append(quote_amount.text)
        print("quote_amounts_list", quote_amounts_list)

        # Closing Date

        closing_dates_list = []
        closing_dates = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-00C")

        for closing_date in closing_dates:
            # print(closing_date.text)
            closing_dates_list.append(closing_date.text)
        print("quote_amounts_list", quote_amounts_list)

        # Stages

        stages_list = []

        stages = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-00D")

        for stage in stages:
            # print(stage.text)
            stages_list.append(stage.text)
        print("stages_list", stages_list)

        # Submitted By
        submitted_by_list = []
        submitted_by_ = self.driver.find_elements(By.CLASS_NAME, "ui-grid-coluiGrid-00E")

        for submitted_by in submitted_by_:
            # print(submitted_by.text)
            submitted_by_list.append(submitted_by.text)
        print("submitted_by_list", submitted_by_list)

        time.sleep(10)
        for name__, service_address__, zip_code__, locator__, quote_id__, quote_amount__, closing_date__, stage__, submitted_by__ in zip(
                seller_name_list, service_address_list, zip_code_list, locators_list, quote_ids_list,
                quote_amounts_list, closing_dates_list, stages_list, submitted_by_list):
            self.data.append({"seller_name": name__, "service_address": service_address__, "zip_code": zip_code__,
                              "locator": locator__, "quote_id": quote_id__, "quote_amount": quote_amount__,
                              "closing_date": closing_date__, "stage": stage__, "submitted_by": submitted_by__})
        write_data_into_json("output/" + self.output_directory_name + "/tq_data", self.data)

        return "output/" + self.output_directory_name + "/tq_data.xlsx"


if __name__ == '__main__':
    TitlequoteScanner().scrape()
