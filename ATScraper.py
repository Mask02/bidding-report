import requests
from bs4 import BeautifulSoup
import json
from FileManager import write_data_into_json, create_output_dir


class ATScraper:

    def __init__(self):

        self.AT_UPCOMMING_SALES_URL = "https://www.armstrongteasdale.com/upcoming-sales/"

        self.data = list()

        self.data_keys = {
            "Sale_date": "col-date",
            "Sale_time": "col-time",
            "Borrower_1_last": "col-name",
            "FileNo": "col-case",
            "PropAddress": "col-address",
            "PropCity": "col-city",
            "County": "col-county",
            "OpeningBid": "col-bid"
        }

        self.output_directory_name = "AT-Scraper-Output"

        create_output_dir(self.output_directory_name)

    def scrape(self):

        response = requests.get(self.AT_UPCOMMING_SALES_URL)

        soup = BeautifulSoup(response.text, "html.parser")

        table_body = soup.find('tbody')

        table_rows = table_body.find_all('tr')

        for row in table_rows:

            row_dict = {
                "Trustee": "",
                "Sale_date": "",
                "Sale_time": "",
                "Borrower_1_last": "",
                "FileNo": "",
                "PropAddress": "",
                "PropCity": "",
                "PropZip": "",
                "County": "",
                "OpeningBid": ""
            }

            row_dict["Trustee"] = "AT, INC"

            for key_1, key_2 in self.data_keys.items():
                row_dict[key_1] = row.find('td', {'class': key_2}).text

            if len(row_dict["FileNo"]) != 0:
                self.data.append(row_dict)

        write_data_into_json("output/" + self.output_directory_name + "/at_data", self.data)

        return "output/" + self.output_directory_name + "/at_data.xlsx"
