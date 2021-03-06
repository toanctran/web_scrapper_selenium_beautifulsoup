from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
    df.to_csv('tuoitre_result_exit.csv', index=False, encoding='utf_8')
    exit(0)


signal(SIGINT, handler)

log.info("***  START SCRAPER   ***")
log.info('')
log.info("Running. Press Ctrl+C to exit")

DRIVER_PATH = 'chromedriver_win32/chromedriver.exe'

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

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

data = []
de_muc_list = ['thoi-su', 'the-gioi', 'phap-luat',
               'kinh-doanh', 'xe', 'nhip-song-tre', 'van-hoa','giai-tri', 'giao-duc', 'khoa-hoc', 'suc-khoe' ] # ['thoi-su', ]
for i in range(0, len(de_muc_list) - 1):
    de_muc = de_muc_list[i]
    n = 1

    found = True
    article_dic = {'category': '', 'article_title': '', 'article_url': '', 'article': '', 'summary': ''}

    log.info(f"Starting scraping the article in {de_muc}")
    while found:
        article_temp = []
        print(f"Getting page {n} of {de_muc} ...")
        url = "https://tuoitre.vn/" + de_muc + "/trang-" + str(n) + ".htm"
        try:
            driver.get(url)
        except NoSuchWindowException:
            driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
            driver.get(url)


        try:
            try:
                # # Wait until the element with CLASS_NAME = product-item present
                # myElem = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'name-news')))

                # Wait 30s to poll the DOM element when trying to find any element (or elements) not immediately available
                driver.implicitly_wait(30)

                log.info(f"Page {n} in {de_muc} is ready!")

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # r = requests.get(url, headers)
                # soup = BeautifulSoup(r.text, 'html.parser')
                news_list = []

                news_list = soup.find_all('div', {'class': 'name-news'})
                assert news_list != [], "Cannot scrape the list of articles"
                assert soup.find('div', {'class': 'main-content-body'}) is None, "This is not article page"

                log.info(f"Found {len(news_list)} articles in page {n} of {de_muc}")

                for news in news_list:
                    try:
                        article_title = news.a['title']
                        article_href = "https://tuoitre.vn" + news.a['href']
                        print(f"Scraping: {news.a['title']}")
                    except Exception as e:
                        log.warning('We got an error when try to process an article')
                        tb = sys.exc_info()[2]
                        log.warning(e.with_traceback(tb))
                        log.warning(news)
                        log.warning("Move to next article")
                        continue

                    try:
                        r = requests.get(article_href, headers)

                        article_page = BeautifulSoup(r.text, 'html.parser')

                        article_dic['summary'] = article_page.find('h2', {'class': 'sapo'}).text

                        article_ = article_page.find('div', {"id": "main-detail-body"}).find_all('p')
                        if article_page.find('div', {'type': 'RelatedOneNews'}) is not None:
                            related_ = article_page.find('div', {'type': 'RelatedOneNews'}).p.text

                        article = ''
                        if article_:
                            for item in article_:
                                if related_ and item.text == related_:
                                    continue
                                else:
                                    article = article + item.text + " "
                    except Exception as e:
                        log.warning(
                            f'We got an error when try to process an article: {article_title} at {article_href}')
                        tb = sys.exc_info()[2]
                        log.warning(e.with_traceback(tb))
                        log.warning("Move to next article")
                        continue

                    article_dic['article'] = article
                    article_dic['category'] = de_muc
                    article_dic['article_title'] = article_title
                    article_dic['article_url'] = article_href

                    if article_dic not in data:
                        article_dic_copy = article_dic.copy()
                        article_temp.append(article_dic_copy)
                        log.info(f"Scraped {len(article_temp)} articles")

                if data != [] and all(elem in article_temp for elem in data) and article_temp != []:
                    log.info(f'Finish scrapping {de_muc}')
                    log.info(f'There are {len(data)} after scraping {de_muc}')
                    log.info('Saving data to tuoitre_result.csv')
                    # Create the Pandas DataFrame with the collected data
                    df = pd.DataFrame(data=data, columns=data[0].keys())
                    # Export and save the DataFrame df to result.csv file
                    df.to_csv('tuoitre_result.csv', index=False, encoding='utf_8')
                    log.info('Successfully saved data to tuoitre_result.csv')
                    log.info(f'Continue to {de_muc_list[i + 1]}')
                    found = False
                    continue

                log.info(f"Starting save {len(article_temp)} articles from article_temp to data")
                log.info(f"Data have {len(data)} articles before saving")
                data = data + article_temp
                log.info(f"Successfully saving {len(article_temp)} articles from article_temp to data")
                log.info(f"***********************************************")
                log.info(f"* Data have {len(data)} articles after saving *")
                print(f"***********************************************")

                n += 1
                log.info('Saving data to tuoitre_result_temp.csv')
                # Create the Pandas DataFrame with the collected data
                df = pd.DataFrame(data=data, columns=data[0].keys())
                # Export and save the DataFrame df to tuoitre_result_temp.csv file
                df.to_csv('tuoitre_result_temp.csv', index=False, encoding='utf_8')
                log.info('Successfully saved data to tuoitre_result_temp.csv')
                log.info(f"**********************************************************")
                log.info(f"* Result_temp.csv have {len(data)} articles after saving *")
                log.info(f"**********************************************************")
                sleep_time = random.randint(5, 10)
                log.info(f'Scrapper sleep in {sleep_time}')
                sleep(sleep_time)
                log.info(f'Scrapped page {n} of {de_muc}. Continue to page {n + 1} of {de_muc} .')
                log.info('')
                log.info("##################################################################")
                log.info('')

            except AssertionError as msg:

                log.warning(f'We got an error when try to process page {n} of {de_muc}')
                log.warning(msg)
                log.warning("Loading took too much time!")
                log.warning("Try to find a See More button")
                url_temp = "https://tuoitre.vn/" + de_muc + "/trang-99.htm"
                driver.get(url_temp)
                driver.implicitly_wait(30)
                click = 0
                count = 0
                while click < 1000:
                    try:

                        driver.execute_script("return arguments[0].scrollIntoView(true);",
                                              WebDriverWait(driver, 10).until(
                                                  EC.visibility_of_element_located((By.CLASS_NAME, "btn-readmore"))))
                        driver.implicitly_wait(20)
                        driver.execute_script("arguments[0].click();",
                                              WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                                                  (By.CLASS_NAME, "btn-readmore"))))
                        click += 1

                    except (TimeoutException, StaleElementReferenceException) as e:
                        log.warning("No more Read More buttons")
                        log.info("Start scraping the new list")

                log.info(f"Finish click Read More button {click} times")

                try:
                    driver.implicitly_wait(30)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    news_list = soup.find_all('div', {'class': 'name-news'})
                    assert news_list != [], "Cannot scrape the list of articles"
                    assert soup.find('div', {'class': 'main-content-body'}) is None, "This is not article page"

                    log.info(f"Found {len(news_list)} articles in page {n} of {de_muc}")

                    for news in news_list:
                        try:
                            article_title = news.a['title']
                            article_href = "https://tuoitre.vn" + news.a['href']
                            print(f"Scraping: {news.a['title']}")
                        except Exception as e:
                            log.warning('We got an error when try to process an article')
                            tb = sys.exc_info()[2]
                            log.warning(e.with_traceback(tb))
                            log.warning(news)
                            log.warning("Move to next article")
                            continue

                        try:
                            r = requests.get(article_href, headers)

                            article_page = BeautifulSoup(r.text, 'html.parser')

                            article_dic['summary'] = article_page.find('h2', {'class': 'sapo'}).text

                            article_ = article_page.find('div', {"id": "main-detail-body"}).find_all('p')
                            if article_page.find('div', {'type': 'RelatedOneNews'}) is not None:
                                related_ = article_page.find('div', {'type': 'RelatedOneNews'}).p.text

                            article = ''
                            if article_:
                                for item in article_:
                                    if related_ and item.text == related_:
                                        continue
                                    else:
                                        article = article + item.text + " "
                        except Exception as e:
                            log.warning(
                                f'We got an error when try to process an article: {article_title} at {article_href}')
                            tb = sys.exc_info()[2]
                            log.warning(e.with_traceback(tb))
                            log.warning("Move to next article")
                            continue

                        article_dic['article'] = article
                        article_dic['category'] = de_muc
                        article_dic['article_title'] = article_title
                        article_dic['article_url'] = article_href

                        if article_dic not in data:
                            article_dic_copy = article_dic.copy()
                            article_temp.append(article_dic_copy)
                            log.info(f"Scraped {len(article_temp)} articles")
                        count += 1
                        if count == 15:
                            sleep_time = random.randint(5, 10)
                            log.info(f'Scrapper sleep in {sleep_time}')
                            sleep(sleep_time)
                            count = 0

                    if data != [] and all(elem in article_temp for elem in data) and article_temp != []:
                        log.info(f'Finish scrapping {de_muc}')
                        log.info(f'There are {len(data)} after scraping {de_muc}')
                        log.info('Saving data to tuoitre_result.csv')
                        # Create the Pandas DataFrame with the collected data
                        df = pd.DataFrame(data=data, columns=data[0].keys())
                        # Export and save the DataFrame df to result.csv file
                        df.to_csv('tuoitre_result.csv', index=False, encoding='utf_8')
                        log.info('Successfully saved data to tuoitre_result.csv')
                        log.info(f'Continue to {de_muc_list[i + 1]}')
                        found = False
                        continue

                    log.info(f"Starting save {len(article_temp)} articles from article_temp to data")
                    log.info(f"Data have {len(data)} articles before saving")
                    data = data + article_temp
                    log.info(f"Successfully saving {len(article_temp)} articles from article_temp to data")
                    log.info(f"***********************************************")
                    log.info(f"* Data have {len(data)} articles after saving *")
                    print(f"***********************************************")

                    log.info('Saving data to tuoitre_result_temp.csv')
                    # Create the Pandas DataFrame with the collected data
                    df = pd.DataFrame(data=data, columns=data[0].keys())
                    # Export and save the DataFrame df to tuoitre_result_temp.csv file
                    df.to_csv('tuoitre_result_temp.csv', index=False, encoding='utf_8')
                    log.info('Successfully saved data to tuoitre_result_temp.csv')
                    log.info(f"**********************************************************")
                    log.info(f"* Result_temp.csv have {len(data)} articles after saving *")
                    log.info(f"**********************************************************")
        
                    log.info(f'Finished scraped {de_muc}. Continue to {de_muc_list[i+1]} .')
                    log.info('')
                    log.info("##################################################################")
                    log.info('')
                    found = False
                    continue

                except AssertionError as msg:
                    log.warning(msg)
                    found = False
                    if i == len(de_muc_list) - 1:
                        log.info("Successfully scraping all the category on TuoiTre")
                        log.info("Quitting driver")
                        driver.quit()
                    else:
                        log.info(f"End of {de_muc}. Move to {de_muc_list[i + 1]}")

        except Exception as e:
            tb = sys.exc_info()[2]
            log.warning(e.with_traceback(tb))
            found = False
            if i == len(de_muc_list) - 1:
                log.info("Successfully scraping all the category on TuoiTre")
                log.info("Quitting driver")
                driver.quit()
            else:
                log.info(f"End of {de_muc}. Move to {de_muc_list[i + 1]}")



# Create the Pandas DataFrame with the collected data
df = pd.DataFrame(data=data, columns=data[0].keys())
# Export and save the DataFrame df to tuoitre.csv file
df.to_csv('tuoitre_result.csv', index=False, encoding='utf_8')
