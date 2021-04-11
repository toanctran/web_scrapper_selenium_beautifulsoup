from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchWindowException

from signal import signal, SIGINT
from sys import exit
import requests
import pandas as pd

from time import time, sleep
import sys
import random

import logging

import logging

log = logging.getLogger('VNE_Scraper')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
fh = logging.FileHandler('vnexpress_scraper.log', encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)
log.propagate = True


def handler(signal_received, frame):
    # Handle any cleanup here
    log.info('SIGINT or CTRL-C detected.Saving data to file')
    df = pd.DataFrame(data=data, columns=data[0].keys())
    # Export and save the DataFrame df to result.csv file
    df.to_csv('vnexpress_result_exit.csv', index=False, encoding='utf_8')
    driver.quit()
    exit(0)


signal(SIGINT, handler)

log.info("START SCRAPER")
log.info("Running. Press Ctrl+C to exit")

DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'

options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

data = []
de_muc_list = ['the-gioi', 'phap-luat', 'kinh-doanh', 'so-hoa', 'doi-song',
               'van-hoa', 'giai-tri', 'giao-duc', 'khoa-hoc', 'suc-khoe',
               'the-thao', 'du-lich', 'thoi-su']

for i in range(0, len(de_muc_list) - 1):
    de_muc = de_muc_list[i]
    waiting_page = 0
    n = 1

    found = True
    article_dic = {'category': '', 'article_title': '', 'article_url': '', 'article': '', 'summary': ''}

    log.info(f"Starting scraping the artice in {de_muc}")
    while found and n < 1000:
        article_temp = []
        log.info(f"Getting page {n} of {de_muc} ...")
        if n == 1:
            url = "https://vnexpress.net/" + de_muc
        else:
            url = "https://vnexpress.net/" + de_muc + "-p" + str(n)

        try:
            driver.get(url)
        except NoSuchWindowException:
            driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
            driver.get(url)

        try:
            # # Wait until the element with CLASS_NAME = product-item present
            # myElem = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'item-news')))

            # Wait 30s to poll the DOM element when trying to find any element (or elements) not immediately available
            driver.implicitly_wait(30)

            log.info(f"Page {n} in {de_muc} is ready!")
        except TimeoutException:
            log.warning("Loading took too much time!")
            log.warning("Continue to next page")
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        news_list = soup.find_all('article', {'class': 'item-news'})
        ignored = []

        if soup.find('div', {'class': 'box-slide-topic'}):
            ignored_links = soup.find('div', {'class': 'box-slide-topic'}).find_all('h3', {'class': 'title-news'})
            for ig in ignored_links:
                ignored.append(ig.a['title'])

        log.info(f"Found {len(news_list)} articles in page {n} of {de_muc}")

        if news_list == [] and i != len(de_muc_list) - 1:
            found = False
            log.info("End of {de_muc}. Move to {de_muc_list[i + 1]}")
        elif news_list == [] and i == len(de_muc_list) - 1:
            log.warning("Successfully scraping all the category on VnExpress")
            log.warning("Quitting driver")
            found = False
            driver.quit()
            continue

        for news in news_list:
            try:
                try:
                    article_title = news.h3.a['title']
                    article_href = news.h3.a['href']
                except Exception as e:
                    log.warning('We got an error when try to process an article')
                    tb = sys.exc_info()[2]
                    log.warning(e.with_traceback(tb))
                    log.info("Try news.h2.a['title'] and news.h2.a['href']")
                    article_title = news.h2.a['title']
                    article_href = news.h2.a['href']
            except Exception as e:
                log.warning('Cannot get the news title')
                tb = sys.exc_info()[2]
                log.warning(e.with_traceback(tb))
                log.info(news)
                log.info('Continue to next News')
                continue

            if ignored != [] and article_title in ignored:
                continue

            if news.find('p', {'class': 'info-ads'}):
                continue

            try:
                print(f"Scraping: {article_title}")
                log.info(f"Scraping: {article_title}")

                article_dic['category'] = de_muc

                article_dic['article_title'] = article_title

                article_dic['article_url'] = article_href

                driver.get(article_href)

                article_page = BeautifulSoup(driver.page_source, 'html.parser')
                article_dic['summary'] = article_page.find('p', {'class': 'description'}).text

                article_ = article_page.find('article', {'class': 'fck_detail'}).find_all('p', {"class": "Normal"})
                article = ''
                if article_:
                    for item in article_:
                        article = article + item.text + " "
                article_dic['article'] = article
            # Handle the error
            except Exception as e:
                log.warning('We got an error when try to process an article')
                tb = sys.exc_info()[2]
                log.warning(e.with_traceback(tb))
                continue

            if article_dic not in data:
                article_dic_copy = article_dic.copy()
                article_temp.append(article_dic_copy)
                log.info(f"Scraped {len(article_temp)} articles")

        if article_temp == []:
            log.info(f'Cannot find new article in page {n} of {de_muc}. Waiting page: {waiting_page} pages')
            waiting_page += 1

        if article_temp == [] and i != len(de_muc_list) - 1 and waiting_page == 5:
            log.info(f"End of {de_muc}. Move to {de_muc_list[i + 1]}")
            found = False
        elif article_temp == [] and i == len(de_muc_list) - 1 and waiting_page == 5:
            log.info("Successfully scraping all the category on VNExpress")
            found = False

        if data != [] and all(elem in article_temp for elem in data) and article_temp != []:
            log.info(f'Finish scrapping {de_muc}')
            log.info(f'There are {len(data)} after scraping {de_muc}')
            log.info('Saving data to vnexpress_result.csv')
            # Create the Pandas DataFrame with the collected data
            df = pd.DataFrame(data=data, columns=data[0].keys())
            # Export and save the DataFrame df to result.csv file
            df.to_csv('vnexpress_result.csv', index=False, encoding='utf_8')
            log.info('Successfully saved data to vnexpress_result.csv')
            log.info(f'Continue to {de_muc_list[i + 1]}')
            found = False
            continue

        log.info(f"Starting save {len(article_temp)} articles from article_temp to data")
        log.info(f"Data have {len(data)} articles before saving")
        data = data + article_temp
        log.info(f"Successfully saving {len(article_temp)} articles from article_temp to data")
        log.info(f"***********************************************")
        log.info(f"* Data have {len(data)} articles after saving *")
        log.info(f"***********************************************")
        sleep_time = random.randint(1, 5)
        log.info(f'Scrapper sleep in {sleep_time}')
        sleep(sleep_time)
        n += 1

        log.info('Saving data to result_temp.csv')
        # Create the Pandas DataFrame with the collected data       
        df = pd.DataFrame(data=data, columns=data[0].keys())
        # Export and save the DataFrame df to result.csv file
        df.to_csv('vnexpress_result_temp.csv', index=False, encoding='utf_8')
        log.info('Successfully saved data to vnexpress_result_temp.csv')
        log.info(f"**********************************************************")
        log.info(f"* vnexpress_result_temp.csv have {len(data)} articles after saving *")
        log.info(f"**********************************************************")
        sleep(sleep_time)
        log.info(f'Scrapped page {n} of {de_muc}. Continue to page {n + 1} of {de_muc} .')
        log.info('')
        log.info("##################################################################")
        log.info('')

# Create the Pandas DataFrame with the collected data       
df = pd.DataFrame(data=data, columns=data[0].keys())
# Export and save the DataFrame df to result.csv file
df.to_csv('vnexpress_result.csv', index=False, encoding='utf_8')
