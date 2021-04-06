from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from signal import signal, SIGINT
from sys import exit

import pandas as pd

from time import time, sleep
import sys
import random

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected.Saving data to file')
    df = pd.DataFrame(data=data, columns=data[0].keys())
    # Export and save the DataFrame df to result.csv file
    df.to_csv('result_exit.csv', index=False, encoding='utf_8')
    exit(0)

signal(SIGINT, handler)

print("Running. Press Ctrl+C to exit")

DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'


options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

data = []
de_muc_list = ['thoi-su', 'the-gioi' , 'phap-luat', 'kinh-doanh', 'so-hoa', 'oto-xe-may', 'doi-song', 'van-hoa','giai-tri', 'giao-duc', 'khoa-hoc', 'suc-khoe', 'the-thao', 'du-lich']

for i in range(0, len(de_muc_list) - 1 ):
    de_muc = de_muc_list[i]
    waiting_page = 0
    n = 1
    found = True
    article_dic = {'category':'', 'article_title' : '', 'article_url':'', 'article':'', 'summary':''}
    
    print(f"Starting scraping the artice in {de_muc}")
    while found:
        article_temp = []
        print(f"Getting page {n} of {de_muc} ...")
        if n == 1:
            url = "https://vnexpress.net/" + de_muc
        else:
            url = "https://vnexpress.net/"+ de_muc + "-p" + str(n)
        driver.get(url)
        try:
            # # Wait until the element with CLASS_NAME = product-item present
            # myElem = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'item-news')))

            # Wait 30s to poll the DOM element when trying to find any element (or elements) not immediately available
            driver.implicitly_wait(30)

            print(f"Page {n} in {de_muc} is ready!")
        except TimeoutException:
            print("Loading took too much time!")
            print("Quitting driver")
            driver.quit()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news_list = soup.find_all('article', {'class':'item-news'})
        print(f"Found {len(news_list)} articles in page {n} of {de_muc}")

        if news_list == [] and i != len(de_muc_list) - 1:
            found = False
            print("End of {de_muc}. Move to {de_muc_list[i + 1]}")
        elif news_list == [] and i == len(de_muc_list) - 1:
            print("Successfully scraping all the category on TuoiTre")
            print("Quitting driver")
            found = False
            driver.quit()
        
        for news in news_list:
            if news.find('p', {'class':'info-ads'}):
                continue
            
            try:
                article_dic['category'] = de_muc
                
                article_dic['article_title'] = news.h3.a['title']
                print(f"Scraping: {news.h3.a['title']}")
                
                article_href = news.h3.a['href']
                article_dic['article_url'] = article_href

                driver.get(article_href)
                driver.implicitly_wait(30)

                article_page = BeautifulSoup(driver.page_source, 'html.parser')
                article_dic['summary'] = article_page.find('p', {'class':'description'}).text
                
                article_ = article_page.find('article', {'class':'fck_detail'}).find_all('p', {"class": "Normal"})
                

                article = ''
                if article_ != []:
                    for item in article_:
                        article = article + item.text + " "
                article_dic['article'] = article
            # Handle the error
            except Exception as e:
                print('We got an error when try to process an article')
                tb = sys.exc_info()[2]
                print(e.with_traceback(tb))
                continue

            if article_dic not in data:
                article_dic_copy = article_dic.copy()
                article_temp.append(article_dic_copy)
                print(f"Scraped {len(article_temp)} articles")

        if article_temp == []:
            print(f'Cannot find new article in page {n} of {de_muc}. Waiting page: {waiting_page} pages')
            waiting_page += 1

        if article_temp == [] and i != len(de_muc_list) - 1 and waiting_page == 5:
            print("End of {de_muc}. Move to {de_muc_list[i + 1]}")
            found = False
            
        elif article_temp == [] and i == len(de_muc_list) - 1  and waiting_page == 5:
            print("Successfully scraping all the category on TuoiTre")
            found = False
            

        if data != [] and all(elem in article_temp for elem in data) and article_temp != [] :
            print("Len of data", len(data))
            print("Len of article_temp", len(article_temp))
            print('Finish scrapping.')
            print('Saving data to result.csv')
            # Create the Pandas DataFrame with the collected data       
            df = pd.DataFrame(data=data, columns=data[0].keys())
            # Export and save the DataFrame df to result.csv file
            df.to_csv('result.csv', index=False, encoding='utf_8')
            print('Successfully saved data to result.csv')
            found = False
            
        print(f"Starting save {len(article_temp)} articles from article_temp to data")
        print(f"Data have {len(data)} articles before saving")
        data = data + article_temp
        print(f"Successfully saving {len(article_temp)} articles from article_temp to data")
        print(f"***********************************************")
        print(f"* Data have {len(data)} articles after saving *")
        print(f"***********************************************")
        sleep_time = random.randint(5, 10)
        print(f'Scrapper sleep in {sleep_time}')
        sleep(sleep_time)
        n += 1

        print('Saving data to result_temp.csv')
        # Create the Pandas DataFrame with the collected data       
        df = pd.DataFrame(data=data, columns=data[0].keys())
        # Export and save the DataFrame df to result.csv file
        df.to_csv('result_temp.csv', index=False, encoding='utf_8')
        print('Successfully saved data to result_temp.csv')
        print(f"**********************************************************")
        print(f"* Result_temp.csv have {len(data)} articles after saving *")
        print(f"**********************************************************")
        sleep(sleep_time)
        print(f'Scrapped page {n} of {de_muc}. Continue to page {n+1} of {de_muc} .')
        print('')
        print("##################################################################")
        print('')
        


# Create the Pandas DataFrame with the collected data       
df = pd.DataFrame(data=data, columns=data[0].keys())
# Export and save the DataFrame df to result.csv file
df.to_csv('result.csv', index=False, encoding='utf_8')