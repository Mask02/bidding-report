import requests
from bs4 import BeautifulSoup
import json
from FileManager import write_data_into_json, create_output_dir

class CTScraper:

    def __init__(self):

        self.CT_URL = "https://www.centretrustee.com/listproperties.php"

        self.data = list()
        
        self.data_keys = ["Sale_date", "Sale_time", "County", "FileNo", "PropAddress", "OpeningBid", "status- DROP DOWN"]

        self.output_directory_name = "CT-Scraper-Output"

        create_output_dir(self.output_directory_name)

    def scrape(self):

        response = requests.get(self.CT_URL)
        
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find_all('table')[1]

        table_rows = list(table.find_all('tr'))[1:]

        for row in table_rows:

            row_dict = {
                    "Trustee": "",
                    "Sale_date": "",
                    "Sale_time": "",
                    "County": "",
                    "PropCity": "",
                    "PropZip":"",
                    "FileNo": "",
                    "PropAddress": "",
                    "OpeningBid": "",
                    "status- DROP DOWN": ""
                    }

            row_dict["Trustee"] = "CENTRE TRUSTEE CORP"

            cols = row.find_all('td')

            for c_index in range(len(cols)):
                row_dict[self.data_keys[c_index]] = cols[c_index].text.strip().replace('\xa0',' ')

            if len(row_dict["FileNo"]) != 0:
                self.data.append(row_dict)
        # Writing data into excel
        write_data_into_json("output/" + self.output_directory_name + "/ct_data", self.data) 

        return "output/" + self.output_directory_name + "/ct_data.xlsx"



