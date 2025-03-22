import tkinter as tk
from ATScraper import ATScraper
from CTScraper import CTScraper
from EPScraper import EPScraper
from LOGScraper import LOGScraper
from MSScraper import MSScraper
from SLScraper import SLScraper
from threading import Thread


def maximize_window(app):
    screen_width = app.winfo_screenwidth()

    screen_height = app.winfo_screenheight()

    app.geometry(f"{screen_width}x{screen_height}")


def execute_all_scrapers():
    at_scraper_thread()
    ct_scraper_thread()
    ep_scraper_thread()
    log_scraper_thread()
    ms_scraper_thread()
    sl_scraper_thread()


def at_scraper():
    try:
        footer.config(text="Scraping AT, INC")
        ATScraper().scrape()
        footer.config(text="Scraping of AT, INC done.")
    except Exception as e:
        footer.config(text="Error occurred")


def at_scraper_thread():
    Thread(target=at_scraper).start()


def ct_scraper():
    try:
        footer.config(text="Scraping CENTRE TRUSTEE")
        CTScraper().scrape()
        footer.config(text="Scraping of CENTRE TRUSTEE CORP done.")
    except Exception as e:
        footer.config(text="Error occurred")


def ct_scraper_thread():
    Thread(target=ct_scraper).start()


def ep_scraper():
    try:
        footer.config(text="Scraping EAST PLAINS")
        EPScraper().scrape()
        footer.config(text="Scraping of EAST PLAINS done.")
    except Exception as e:
        footer.config(text="Error occurred")


def ep_scraper_thread():
    Thread(target=ep_scraper).start()


def log_scraper():
    try:
        footer.config(text="Scraping LOGS INC")
        LOGScraper().scrape()
        footer.config(text="Scraping of LOGS INC done.")
    except Exception as e:
        footer.config(text="Error occurred")


def log_scraper_thread():
    Thread(target=log_scraper).start()


def ms_scraper():
    try:
        footer.config(text="Scraping MS FIRM")
        MSScraper().scrape()
        footer.config(text="Scraping of MS FIRM done.")
    except Exception as e:
        footer.config(text="Error occurred")


def ms_scraper_thread():
    Thread(target=ms_scraper).start()


def sl_scraper():
    try:
        footer.config(text="Scraping SOUTH LAW")
        SLScraper().scrape()
        footer.config(text="Scraping of SOUTH LAW done.")
    except Exception as e:
        footer.config(text="Error occurred")


def sl_scraper_thread():
    Thread(target=sl_scraper).start()


app = tk.Tk()

app.title("Bidding Report Scraper")

header = tk.Label(app, text="Bidding Report Scraper", font=("Helvetica", 20, "bold"), foreground='green')

btn_all = tk.Button(app, text="EXECUTE ALL", command=execute_all_scrapers, width=30, background='green',
                    foreground='white')
btn_at = tk.Button(app, text='AT, INC', command=at_scraper_thread, width=30, background='green', foreground='white')
btn_ct = tk.Button(app, text='CENTRE TRUSTEE CORP', command=ct_scraper_thread, width=30, background='green',
                   foreground='white')
btn_ep = tk.Button(app, text='EAST PLAINS', command=ep_scraper_thread, width=30, background='green', foreground='white')
btn_log = tk.Button(app, text='LOGS', command=log_scraper_thread, width=30, background='green', foreground='white')
btn_ms = tk.Button(app, text='MS FIRM', command=ms_scraper_thread, width=30, background='green', foreground='white')
btn_sl = tk.Button(app, text='SOUTH LAW', command=sl_scraper_thread, width=30, background='green', foreground='white')

footer = tk.Label(app, text="Scraping Status", font=("Helvetica", 8), background="black", fg="white", width=30, padx=18,
                  pady=3)

header.pack(pady=10)
btn_at.pack(pady=10)
btn_ct.pack(pady=10)
btn_ep.pack(pady=10)
btn_log.pack(pady=10)
btn_ms.pack(pady=10)
btn_sl.pack(pady=10)
btn_all.pack(pady=10)
footer.pack(pady=20)

maximize_window(app)

app.mainloop()
