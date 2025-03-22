import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
from FileManager import write_data_into_json, create_output_dir
from Logger import log
import os
import glob

class SLScraper:
    def __init__(self):
        self.BASE_URL = "https://www.southlaw.com"
        self.SL_DOWNLOAD_URL = self.BASE_URL + "/download/"
        self.file_names = []
        self.data = []
        # Restore the keys list
        self.keys = ["PropAddress", "PropCity", "PropZip", "Sale_date", "Sale_time", 
                     "continued_date", "OpeningBid", "Courthouse", "Civil Case No.", "Firm File#"]
        self.output_directory_name = "SL-Scraper-Output"
        create_output_dir(self.output_directory_name)
        
        output_dir = "output/" + self.output_directory_name
        for ext in (".pdf", ".json"):
            files_to_remove = glob.glob(os.path.join(output_dir, f"*{ext}"))
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    print(f"Deleted existing file: {file_path}")
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")

    def scrape(self):
        response = requests.get(self.SL_DOWNLOAD_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        files_headings = soup.find_all('h4')
        files_links = [self.BASE_URL + heading.find('a')['href'] for heading in files_headings]
        self.download_pdfs(files_links)
        for filename in self.file_names:
            self.read_pdfs(filename)
        log(f"SLScraper: Final data before writing to JSON (length: {len(self.data)}): {self.data}")
        write_data_into_json("output/" + self.output_directory_name + '/sl_data', self.data)
        return "output/" + self.output_directory_name + '/sl_data.json'

    def download_pdfs(self, links):
        for lnk in links:
            response = requests.get(lnk)
            file_name = "output/" + self.output_directory_name + "/" + lnk.split("/")[-1]
            self.file_names.append(file_name)
            with open(file_name, "wb") as out:
                out.write(response.content)

    def update_data(self, record, county):
        row_dict = {
            "Trustee": "SOUTHLAW",
            "Sale_date": "",
            "Sale_time": "",
            "continued_date": "N/A",
            "continued_time": "",
            "County": county,
            "Civil Case No.": "",
            "FileNo": "",
            "OpeningBid": None,
            "PropAddress": "",
            "PropCity": "",
            "PropZip": "",
            "Courthouse": ""
        }
        
        try:
            for key, value in zip(self.keys, record):
                if value is None:
                    value = ""
                if key == "Firm File#":
                    row_dict["FileNo"] = value
                elif key == "continued_date" and value != "N/A":
                    parts = value.split(" ", 1)
                    row_dict["continued_date"] = parts[0]
                    row_dict["continued_time"] = parts[1] if len(parts) > 1 else ""
                elif key == "OpeningBid" and value and value != "N/A":
                    row_dict[key] = float(re.sub(r'[^\d.]', '', value)) if value else None
                else:
                    row_dict[key] = value
            
            if row_dict["PropAddress"]:
                self.data.append(row_dict)
                log(f"SLScraper: Added record: {row_dict}")
            else:
                log(f"SLScraper: Skipped record (no address): {row_dict}")
        except Exception as e:
            log(f"SLScraper: Error in update_data with record {record}: {str(e)}")

    def read_pdfs(self, filename):
        with open(filename, "rb") as pdf_file:
            pdf = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf.pages)
            current_county = None
            record = []
            
            log(f"SLScraper: Reading PDF: {filename}, {num_pages} pages")
            for page_num in range(num_pages):
                page = pdf.pages[page_num]
                text = page.extract_text()
                log(f"SLScraper: Raw text from page {page_num + 1}: {text}")
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                data_lines = lines  # Process all lines
                log(f"SLScraper: Page {page_num + 1} has {len(data_lines)} data lines: {data_lines}")
                
                for i, line in enumerate(data_lines):
                    try:
                        # County detection
                        if (len(line.split()) <= 2 and line.isupper() and 
                            not any(c.isdigit() for c in line) and 
                            (i == 0 or (i > 0 and data_lines[i-1] == ""))):
                            if record:
                                self.process_record(record, current_county)
                            current_county = line
                            record = []
                            log(f"SLScraper: Found county: {current_county}")
                            continue
                        
                        # Start or continue record
                        if (re.match(r'^\d+\s+[A-Za-z]', line) or "APT" in line.upper() or "UNIT" in line.upper()):
                            if record:
                                self.process_record(record, current_county)
                            record = [line]
                            log(f"SLScraper: New record started with address: {line}")
                        elif record:
                            record.append(line)
                            log(f"SLScraper: Added to record: {line}")
                        
                        if i == len(data_lines) - 1 and record:
                            self.process_record(record, current_county)
                            record = []
                            
                    except Exception as e:
                        log(f"SLScraper: Error processing line '{line}': {str(e)}")
            
            if record:
                self.process_record(record, current_county)

    def process_record(self, record, county):
        try:
            if not record:
                log(f"SLScraper: Empty record skipped")
                return
                
            processed = [""] * len(self.keys)
            processed[0] = record[0]  # PropAddress
            
            for i, line in enumerate(record[1:], start=1):
                line = line.strip()
                if not line:
                    continue
                if i == 1 and not re.match(r'^\d', line):  # Likely PropCity
                    processed[1] = line
                elif re.match(r'^\d{5}(-\d{4})?$', line):  # PropZip
                    processed[2] = line
                elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}', line):  # Sale_date or continued_date
                    if not processed[3]:
                        processed[3] = line
                    else:
                        processed[5] = line
                elif re.match(r'^\d{1,2}:\d{2}\s?(AM|PM|am|pm)$', line, re.IGNORECASE):  # Sale_time
                    processed[4] = line
                elif re.search(r'[\$S]\d+(,\d+)*(\.\d+)?', line):  # OpeningBid
                    processed[6] = line
                elif "COURT" in line.upper() and not processed[7]:  # Courthouse
                    processed[7] = line
                elif re.match(r'^\d{2,4}-.*', line) and not processed[8]:  # Civil Case No.
                    processed[8] = line
                elif line.strip() and not processed[9]:  # Firm File#
                    processed[9] = line
            
            log(f"SLScraper: Processed record: {processed}")
            self.update_data(processed, county)
                
        except Exception as e:
            log(f"SLScraper: Error processing record {record}: {str(e)}")

if __name__ == "__main__":
    bot = SLScraper()
    bot.scrape()