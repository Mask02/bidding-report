from flask import Flask, send_file
from ATScraper import ATScraper
from CTScraper import CTScraper
from EPScraper import EPScraper
from LOGScraper import LOGScraper
from MSScraper import MSScraper
from SLScraper import SLScraper
from TitlequoteScanner import TitlequoteScanner
import schedule
from threading import Thread
import time
from Logger import log

app = Flask(__name__)

@app.route('/ep')
def ep_scraper():
    return send_file("output/EP-Scraper-Output/ep_data.json")


@app.route('/log')
def log_scraper():
    return send_file("output/LOG-Scraper-Output/log_data.json")


@app.route('/ms')
def ms_scraper():
    return send_file('output/MS-Scraper-Output/MS.json')


@app.route('/sl')
def sl_scraper():
    return send_file('output/SL-Scraper-Output/sl_data.json')


@app.route('/tq')
def tq_scraper():
    return send_file('output/TitlequoteScanner-Output/tq_data.json')


def scraping():

    try:
        EPScraper().scrape()
    except Exception as e:
        log("EPScraper:" + str(e))

    try:
        LOGScraper().scrape()
    except Exception as e:
        log("LOGScraper:" + str(e))

    try:
        MSScraper().scrape()
    except Exception as e:
        log("MSScraper:" + str(e))

    try:
        SLScraper().scrape()
    except Exception as e:
        log("SLScraper:" + str(e))

    try:
        TitlequoteScanner().scrape()
    except Exception as e:
        log("TitlequoteScanner:" + str(e))


def scraping_thread():
    Thread(target=scraping).start()


def schedule_script():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(2).hours.do(scraping_thread)

if __name__ == "__main__":
    Thread(target=scraping_thread).start()
    Thread(target=schedule_script).start()
    app.run("0.0.0.0", port=80)
