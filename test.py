from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.opera.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
import requests
from signal import signal, SIGINT
from sys import exit

import pandas as pd

from time import time, sleep
import sys
import random
import logging

log = logging.getLogger('TuoiTreScraper')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
fh = logging.FileHandler('tuoitre_scraper.log', encoding='utf-8')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
log.propagate = True


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected.Saving data to file')
    df = pd.DataFrame(data=data, columns=data[0].keys())
    # Export and save the DataFrame df to result.csv file
    df.to_csv('result_exit.csv', index=False, encoding='utf_8')
    exit(0)


signal(SIGINT, handler)

log.info("***  START SCRAPER   ***")
log.info('')
log.info("Running. Press Ctrl+C to exit")

DRIVER_PATH = 'operadriver_win64/operadriver.exe'

uastrings = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2820.59 Safari/537.36"
    ]

headers = {
    'User-Agent': random.choice(uastrings),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'DNT': '1'
}

options = Options()
options.headless = False
options.add_argument("--incognito")

driver = webdriver.Opera(options=options, executable_path=DRIVER_PATH)

url_temp = "https://tuoitre.vn/" + 'the-gioi' + "/trang-" + str(100 - 1) + ".htm"
driver.get(url_temp)
driver.implicitly_wait(30)
click = 1
try:

    while click < 1000:

        try:
            driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME,"btn-readmore"))))
            driver.execute_script("arguments[0].click();", WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.CLASS_NAME,"btn-readmore"))))
            print("View More button clicked")
        except (TimeoutException, StaleElementReferenceException) as e:
            print("No more View More buttons")
            break

        # driver.find_element_by_class_name('btn-readmore').click()
        driver.implicitly_wait(30)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news_list = soup.find_all('div', {'class': 'name-news'})
        assert news_list != [], "Cannot scrape the list of articles"
        click += 1
except AssertionError as msg:
    print(msg)
    print(f"At click: {click}")
    print(soup)
