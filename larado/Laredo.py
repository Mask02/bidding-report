from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.webdriver.common.action_chains import ActionChains
import requests
from slugify import slugify
import csv
import json
import time 
import os

class Laredo:

    def __init__(self):

        self.flow_start_time = time.time()
        
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless") # Run chrome in headless mode
        chrome_options.add_argument("--disable-gpu") # Disable GPU acceleration (recommended)
        chrome_options.add_argument("--no-sandbox") # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource issues
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.execute_cdp_cmd("Network.enable", {})

        self.action_chains = ActionChains(self.driver)

        self.WAIT_DURATION = 5
        self.wait = WebDriverWait(self.driver, self.WAIT_DURATION)

        self.OUTPUT_DIRECTORY = "files"
        os.makedirs(self.OUTPUT_DIRECTORY, exist_ok=True)

        self.flow_log = {}

    def __write_flow_logs(self):

        try:
            
            with open('lardo-flow-logs.json', 'w') as f:

                f.write(json.dumps(self.flow_log))

        except Exception as e:

            print('Error in __write_flow_logs():', e)

            self.__write_log(e)

    def __write_log(self, msg):

        try:
            with open('laredo.logs', 'a') as f:
                f.write(str(msg) + "\n\n\n")
        except Exception as e:
            print("Error in write_log():", e)

    def __intercept(self):

        data = {"docs_list": [], "auth_token": ""}

        try:

            logs = self.driver.get_log("performance")

            for entry in logs:
                try:
                    message = json.loads(entry["message"])["message"]
                    if message["method"] == "Network.responseReceived":
                        request_id = message["params"]["requestId"]
                        url = message["params"]["response"]["url"]
                        try:
                            # Fetch response body using the extracted requestId
                            if url.endswith('api/advance/search'):
                                response_body = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                                print(f"URL: {url}")
                                response_body = response_body.get("body")
                                docs_data = json.loads(response_body)
                                if "documentList" in docs_data:
                                    data["docs_list"] = docs_data["documentList"]
                                
                        except Exception as e:
                            print(f"Error retrieving body for {url}: {e}")
                    
                    elif message["method"] == "Network.requestWillBeSent":

                        url = message["params"]["documentURL"]

                        if url.endswith('/LaredoAnywhere/LaredoAnywhere.WebSite/'):
                            if "Authorization" in message["params"]["request"]["headers"]:
                                data["auth_token"] = [message["params"]["request"]["headers"]["Authorization"]]

                except Exception as ex:
                    print("Error parsing log entry:", ex)
                    self.__write_log(ex)
        
        except Exception as e:

            print("Error in intercept_resposne()")
            self.__write_log(e)

        return data
        
    def __login(self):

        is_logged_in = False

        try:

            self.driver.get('https://www.laredoanywhere.com/')

            username = self.__wait_for_element("//input[@id='username']", is_multiple_elements=False)

            if not username:
                self.__login()

            username.send_keys("YOUGOGIRL")

            password = self.__wait_for_element("//input[@id='password']", False)

            password.send_keys("WEINERT!")

            login = self.__wait_for_element("//button", False)

            login.click()
            
            time.sleep(10)
            
            if self.__wait_for_element("//div[contains(@class, 'button-wrapper')]", is_multiple_elements=False):

                is_logged_in = True

                self.flow_log["login_status"] = "success"        

        except Exception as e:

            print("Error in login()")

            self.__write_log(e)

            self.flow_log["login_status"] = "failed"

        return is_logged_in

    def __connect_county(self, county_name, county):

        try:

            time.sleep(5)

            self.action_chains.move_to_element(county).perform()
            
            county.click() 

            while True:

                disconnect_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@type='submit']")))

                if disconnect_button.text == "Disconnect":
                    self.flow_log[county_name] = {"connected": "success"}
                    break
        
        except Exception as e:

            print("Error in connect_county()")

            self.__write_log(e)

            self.flow_log[county_name] = {"connected": "failed"}

    def __close_popup(self):

        try:

            time.sleep(5)

            close_popup = self.__wait_for_element("//i[contains(@class, 'fa-xmark')]", is_multiple_elements=False)

            if close_popup:
                close_popup.click()
            else:
                print("Close popup not found.")
        
        except Exception as e:

            print("Error in close_popup()")

            self.__write_log(e)

    def __disconnect_county(self, county_name):

        try:

            disconnect_button = self.__wait_for_element("//button[@type='submit']", False)

            if disconnect_button.text == 'Disconnect':
                disconnect_button.click()
                self.flow_log[county_name]["disconnected"] = "success"
                print("Disconnected")

            time.sleep(10)
            
        except Exception as e:

            print("Error in disconnect_county()")

            self.__write_log(e)

            self.flow_log[county_name]["disconnected"] = "failed"

    def __logout(self):

        try:
            logout_button = list(self.__wait_for_element("//button[contains(@class,'nav-button')]", True))[-1]

            if 'Sign out' in logout_button.text:

                logout_button.click()

                print("Sign out clicked.")

                time.sleep(5)

                yes_button = self.__wait_for_element("//div[contains(@class,'mobile-dialog-button')]", False)

                yes_button.click()

                print("Signed out.")

                self.flow_log["logout"] = "success"

                time.sleep(5)

        except Exception as e:

            print("Error in logout()")

            self.__write_log(e)

            self.flow_log["logout"] = "failed"

    def __get_week_start_date(self):

        week_start_date = datetime.today() - timedelta(days=6)
        return week_start_date.strftime("%m%d%Y")
 
    def __fill_form(self, county_name):

        try:

            time.sleep(5)

            # Enter Start Date
            start_date = self.__wait_for_element("//input[@placeholder='Enter a start date']", is_multiple_elements=False)            
            start_date.send_keys(self.__get_week_start_date())
            time.sleep(2)
            
            # Select 'Search Group'; 'Appointment Successor'
            search_dropdown_div = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//p-dropdown[@formcontrolname='selectedSearchGroup']")))
            search_dropdown_div.click()
            time.sleep(4)
            search_input_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@class, 'p-dropdown-filter')]")))
            if county_name == "Jefferson County":
                search_input_field.send_keys('APPOINTMENT')
            else:
                search_input_field.send_keys('Successor')
            time.sleep(2)
            first_search_option = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//li[@role='option']")))
            first_search_option.click()
            time.sleep(2)

            # Click on 'Run' Button to start search
            run_search_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class,'run-btn')]")))
            run_search_button.click()

            time.sleep(20)
        
        except Exception as e:

            print("Error in fill_form()")
            self.__write_log(e)
    
    def __clean_data(self, county_slug, docs_list):

        doc_id = 1

        new_docs_list = []

        for doc in docs_list:

            try:

                new_doc = {"id": "", "Doc Number": "", "Party": "", "Book & Page": "", 
                        "Doc Date": "", "Recorded Date": "", "Doc Type": "", "Assoc Doc": "", 
                        "Legal Summary": "", "Consideration": "", 
                        "Pages": ""}

                new_doc["id"] = f"{county_slug}-{doc_id}"

                new_doc["Doc Number"] = str(doc["userDocNo"]) if "userDocNo" in doc else ""

                new_doc["Party"] = (doc["partyOne"] if "partyOne" in doc and doc["partyOne"] else "") + (f' ({doc["partyOneType"]})' if "partyOneType" in doc and doc["partyOneType"] else "")

                new_doc["Book & Page"] = doc["bookPage"] if "bookPage" in doc else ""

                new_doc["Doc Type"] = doc["docType"] if "docType" in doc else ""

                new_doc["Legal Summary"] = doc["legalSummary"] if "legalSummary" in doc else ""

                new_doc["Assoc Doc"] = doc["assocDocSummary"] if "assocDocSummary" in doc else ""

                new_doc["Consideration"] = f'${doc["consideration"]}' if "consideration" in doc and doc["consideration"] != None else ""

                new_doc["Pages"] = doc["pages"] if "pages" in doc else ""

                # doc date

                if "docDate" in doc:
                    
                    if doc["docDate"]:
                        try:
                            doc_datetime = datetime.strptime(doc["docDate"], "%Y-%m-%dT%H:%M:%S")

                            new_doc["Doc Date"] = doc_datetime.strftime("%m/%d/%Y")
                        except:
                            new_doc["Doc Date"] = ""
                    else:
                        new_doc["Doc Date"] = ""

                # doc recorded date

                if "docRecordedDateTime" in doc:

                    if doc["docRecordedDateTime"]:
                        try:
                            doc_datetime = datetime.strptime(doc["docRecordedDateTime"], "%Y-%m-%dT%H:%M:%S")

                            new_doc["Recorded Date"] = doc_datetime.strftime("%m/%d/%Y, %I:%M %p")
                        except:
                            new_doc["Recorded Date"] = ""
                    else:
                        new_doc["Recorded Date"] = ""

                # append new doc in new list

                new_docs_list.append(new_doc)

            except Exception as e:

                print("Error in cleaning docs:", e)

                self.__write_log(e)

            doc_id += 1

        return new_docs_list

    def __write_csv(self, data, filename):

        try:

            with open(f"{self.OUTPUT_DIRECTORY}/{filename}.csv", mode='w', newline="") as file:

                field_names = data[0].keys()

                writer = csv.DictWriter(file, fieldnames=field_names)

                # Write Headers
                writer.writeheader()

                # Write the rows
                writer.writerows(data)

            print(f"CSV file '{filename}' has been created successfully.")

        except Exception as e:

            print("Error in write_csv():", e)

    def __get_counties(self):

        counties = []

        try:

            counties = self.__wait_for_element("//div[contains(@class, 'button-wrapper')]", is_multiple_elements=True)

            if not counties:
                self.__get_counties()

        except Exception as e:

            print("Error in __get_counties():", e)

            self.__write_log(e)

        return list(counties)
    
    def __wait_for_element(self, element_xpath, is_multiple_elements):

        for _ in range(5):

            try:
                if is_multiple_elements:
                    return self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, element_xpath)))
                else:
                    return self.wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
            except:
                print(f"'{element_xpath}' not found.")

        return False

    def get_grouped_data(self, clean_data):

        grouped_data = {}

        try:

            for record in clean_data:

                doc_number = record["Doc Number"]

                if doc_number in grouped_data:
                    grouped_data[doc_number].append(record)
                else:
                    grouped_data[doc_number] = [record]
        
        except Exception as e:

            print("Error in get_grouped_data():", e)

        return grouped_data

    def get_combined_records(self, auth_token, doc_id_map, grouped_data):

        new_records_list = []

        try:

            # Extract records from group; Identify max values for parties, addresses, and parcels

            records_list = []

            max_parties = max_addresses = max_parcels = 0

            for doc_number in grouped_data:
                
                records = grouped_data[doc_number]

                old_record = records[0]

                old_record.update(self.get_doc_details(auth_token, doc_id_map[doc_number]))

                records[0] = old_record

                if len(records) > max_parties:

                    max_parties = len(records)
                
                if len(old_record["addresses"]) > max_addresses:

                    max_addresses = len(old_record["addresses"])

                if len(old_record["parcels"]) > max_parcels:

                    max_parcels = len(old_record["parcels"])

                records_list.append(records)

            # Write existing values; Create dummy values if existing values are less than max values
            def combine_dummies(max_entities, key_value, linked_records, new_record):

                if key_value == "Party":
                    all_values = [r["Party"] for r in linked_records]
                    required_dummies = max_entities - len(linked_records)
                    all_values +=  [''] * required_dummies
                else:
                    all_values = linked_records[0][key_value]
                    required_dummies = max_entities - len(linked_records[0][key_value])
                    all_values +=  [''] * required_dummies
                
                if key_value == "addresses":
                    key_value = "Address"
                elif key_value == "parcels":
                    key_value = "Parcel"

                for index in range(len(all_values)):

                    new_record[f"{key_value}{index+1}"] = all_values[index]

            # Create a new record by including new columns
            max_parties = 6 # Remove it if you want to keep the max_parties equal to actual max instances in data.
            for linked_records in records_list:

                new_record = {}

                old_record = linked_records[0]

                for key in old_record:

                    if key == "Party":

                        combine_dummies(max_parties, key, linked_records, new_record)

                    elif key == "addresses":

                        combine_dummies(max_addresses, key, linked_records, new_record)

                    elif key == "parcels":

                        combine_dummies(max_parcels, key, linked_records, new_record)

                    else:

                        new_record[key] = old_record[key]

                new_records_list.append(new_record)

        except Exception as e:

            print("Error in get_combined_records():", e)
        
        return new_records_list
    
    def get_doc_details(self, auth_token, search_doc_id):

        doc_details = {"addresses": [], "parcels": []}

        try:

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": f"{auth_token}",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Cookie": "_ga=GA1.2.37543664.1740670365; _gid=GA1.2.48897604.1741206393; _ga_W87ZSLCJ4D=GS1.2.1741244282.13.1.1741244599.0.0.0",
                "Sec-Fetch-Dest": 'empty',
                "Sec-Fetch-Mode": 'cors',
                "Sec-Fetch-Site": 'same-origin',
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
                "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
                "sec-ch-ua-mobile": '?0',
                "sec-ch-ua-platform": '"Windows"',
            }

            data = {"searchDocId":search_doc_id,"searchResultId":None,"searchResultAuthCode":None}
            
            response = requests.post("https://www.laredoanywhere.com/LaredoAnywhere/LaredoAnywhere.WebService/api/docDetail",headers=headers, json=data)

            json_response = response.json()

            time.sleep(2)

            if "document" in json_response and "legalList" in json_response["document"]:

                legalList = json_response["document"]["legalList"]

                address_list = list()

                parcel_list = list()

                for legal in legalList:

                    if legal["legalType"] == "A":

                        address_list.append(legal["description"])
                    
                    elif legal["legalType"] == "P":

                        parcel_list.append(legal["description"])

                doc_details["addresses"] = address_list

                doc_details["parcels"] = parcel_list

        except Exception as e:

            print("Error in get_doc_details():", e)

        return doc_details
    
    def get_map(self, data_list):

        # Record User Doc Number -> Record Search Id

        data_map = {} 

        try:

            for data in data_list:

                if data["userDocNo"] not in data_map:

                    data_map[data["userDocNo"]] = data["searchDocId"]
        
        except Exception as e:

            print("Error in get_map():", e)

        return data_map

    def extract_data(self):

        try:
            
            if not self.__login():
                return

            available_counties = self.__get_counties()

            total_counties = len(available_counties)

            print("Total Counties:", total_counties)

            current_county = 0

            while current_county < total_counties:

                try:

                    county = available_counties[current_county]

                    county_name = json.loads(county.get_attribute('id'))["Name"]

                    county_slug = slugify(county_name)

                    print(f"Scraping {county_name}")

                    self.__connect_county(county_name, county)

                    self.__close_popup()

                    self.__fill_form(county_name)

                    intercept_data = self.__intercept()

                    docs_list = intercept_data["docs_list"]

                    auth_token = intercept_data["auth_token"][0]

                    print("Token:", auth_token)

                    cleaned_docs_list = self.__clean_data(county_slug, docs_list)

                    if cleaned_docs_list:

                        grouped_data = self.get_grouped_data(cleaned_docs_list)

                        doc_id_map = self.get_map(docs_list)

                        combined_records = self.get_combined_records(auth_token, doc_id_map, grouped_data)

                        if combined_records:

                            self.__write_csv(combined_records, county_slug)

                            self.flow_log[county_name]["data"] = "saved"
                        
                        else:
                            
                            print(f"Csv not saved. Empty combined records for '{county_name}'")

                            self.flow_log[county_name]["data"] = "not saved"

                    self.__disconnect_county(county_name)

                except Exception as e:

                    print("Error in iterating counties:", e)

                available_counties = self.__get_counties()

                total_counties = len(available_counties)

                current_county += 1

            self.__logout()

            self.driver.quit()

            self.flow_log["time_taken"] = time.time() - self.flow_start_time

            self.__write_flow_logs()

        except Exception as e:

            print("Error in extract_data():", e)

            self.__write_log(e)


Laredo().extract_data()