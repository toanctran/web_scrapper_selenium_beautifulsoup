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



DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'


options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

article_href = 'https://vnexpress.net/hanh-khach-khoc-vi-bi-hieu-nham-gay-tai-nan-tau-dai-loan-4258632.html'

driver.get(article_href)
driver.implicitly_wait(30)

article_page = BeautifulSoup(driver.page_source, 'html.parser')

article_ = article_page.find('article', {'class':'fck_detail'}).find_all('p', {"class": "Normal"})
# print(article_page.find('article', {'class':'fck_detail'}))
# print(article_)

article = ''

for item in article_:
    article = article + item.text + " "

print(article)

