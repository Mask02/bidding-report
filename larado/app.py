from flask import Flask, send_from_directory
from Laredo import Laredo
import schedule
import time
from threading import Thread

app = Flask(__name__)

@app.route('/laredoanywhere/<filename>')
def download(filename):
    return send_from_directory("files", filename+".csv", as_attachment=True)

def run_scraper():

    laredo = Laredo()

    laredo.extract_data()

def check_for_pending_tasks():

    while True:

        schedule.run_pending()
        time.sleep(60) # Check every minute

schedule.every().day.at("10:00").do(run_scraper)
schedule.every().day.at("10:00").do(run_scraper)

Thread(target=run_scraper).start()
Thread(target=check_for_pending_tasks).start()

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=80)