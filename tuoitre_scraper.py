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
    print('SIGINT or CTRL-C detected.')
    print("Saving data to file")
    df = pd.DataFrame(data=data, columns=data[0].keys())
    # Export and save the DataFrame df to result.csv file
    df.to_csv('result_exit.csv', index=False, encoding='utf_8')
    print("Successfully save data to result_exit.csv")
    print("Exiting gracefully")
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
de_muc_list = ['thoi-su', 'the-gioi' ] #, 'phap-luat', 'kinh-doanh', 'cong-nghe', 'xe', 'nhip-song-tre', 'van-hoa','giai-tri', 'giao-duc', 'khoa-hoc', 'suc-khoe' ]
for de_muc in de_muc_list:
    n = 1
    article_dic = {'category':'', 'article_title' : '', 'article_url':'', 'article':'', 'summary':''}
    
   
    print(f"Starting scraping the artice in {de_muc}")
    while n < 3:
        article_temp = []
        print(f"Getting page {n} of {de_muc} ...")  
        url = "https://tuoitre.vn/" + de_muc + "/trang-" + str(n) + ".htm"
        driver.get(url)
        try:
            # # Wait until the element with CLASS_NAME = product-item present
            # myElem = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'news-item')))

            # Wait 30s to poll the DOM element when trying to find any element (or elements) not immediately available
            driver.implicitly_wait(30)

            print(f"Page {n} in {de_muc} is ready!")
        except TimeoutException:
            print("Loading took too much time!")
            print("Quitting driver")
            driver.quit()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        news_list = soup.find_all('div', {'class':'name-news'})

        for news in news_list:
            try:
                article_dic['category'] = de_muc
                try:
                    article_dic['article_title'] = news.a['title']
                except:
                    continue
                article_href = "https://tuoitre.vn" + news.a['href']
                article_dic['article_url'] = article_href

                driver.get(article_href)
                article_page = BeautifulSoup(driver.page_source, 'html.parser')
                article_dic['summary'] = article_page.find('h2', {'class':'sapo'}).text
                
                article_ = article_page.find('div', {"id": "main-detail-body"}).find_all('p')
                if article_page.find('div', {'type':'RelatedOneNews'}) != None:
                    related_ = article_page.find('div', {'type':'RelatedOneNews'}).p.text

                article = ''
                if article_ != []:
                    for item in article_:
                        if related_ != None and item.text == related_:
                            continue
                        else:
                            article = article + item.text + " "
                article_dic['article'] = article
            # Handle the error
            except Exception as e:
                print('We got an error when try to process a article')
                print(news)
                tb = sys.exc_info()[2]
                print(e.with_traceback(tb))

            if article_dic not in data:
                article_dic_copy = article_dic.copy()
                article_temp.append(article_dic_copy)
                print(f"Scraped {len(article_temp)} articles")

        if data != [] and all(elem in article_temp for elem in data) and article_temp != [] :
            print("Len of data", len(data))
            print("Len of article_temp", len(article_temp))
            print('Finish scrapping.')
            driver.quit()
            break
        print(f"Starting save {len(article_temp)} articles from article_temp to data")
        print(f"Data have {len(data)} articles before saving")
        data = data + article_temp
        print(f"Successfully saving {len(article_temp)} articles from article_temp to data")
        print(f"Data have {len(data)} articles after saving")
        sleep_time = random.randint(1, 5)
        print(f'Scrapper sleep in {sleep_time}')
        sleep(sleep_time)
        print(f'Scrapped page {n} of {de_muc}. Continue to page {n+1} of {de_muc} .')
            
        n += 1
        


# Create the Pandas DataFrame with the collected data       
df = pd.DataFrame(data=data, columns=data[0].keys())
# Export and save the DataFrame df to result.csv file
df.to_csv('result.csv', index=False, encoding='utf_8')

            

        

        