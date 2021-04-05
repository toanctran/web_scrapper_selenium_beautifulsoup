from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

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
n = 1
data = []

while True:

    product_dic = {'product_title' : '', 'product_url':''}
    product_temp = []

    url = "https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846?&page="+str(n)
    driver.get(url)
    try:
        # # Wait until the element with CLASS_NAME = product-item present
        # myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-item')))

        # Wait 30s to poll the DOM element when trying to find any element (or elements) not immediately available
        driver.implicitly_wait(30)
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")


    # # Scroll the window to the end of webpage
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scripts = soup.find_all('script', {'type':'application/ld+json'})
   
    print(f'Start scrapping the product information in page {n}')

    for script in scripts[1:-2]:
        
        product_info = eval(script.string)

        try:
            # Find product title by data-title
            product_dic['product_title'] = product_info['name']
            
            # Find product url by href
            # product_url = 'https://tiki.vn' + product['href']
            product_dic['product_url'] = product_info['url']
            
        # Handle the error
        except Exception as e:
            print('We got an error when try to process a product')
            tb = sys.exc_info()[2]
            print(e.with_traceback(tb))

        # Append the product to temporary product list
        product_copy = product_dic.copy()
        product_temp.append(product_copy)

        # Click the arrow to go to next page
        driver.find_element_by_class_name('icon-arrow-back').click()
    
    # If temporary product list is not in product data list, add temporary product list and continue the while loop. Otherwhise, break the loop
    if data != [] and all(elem in product_temp for elem in data):
        print('Finish scrapping.')
        driver.quit()
        break
    
    # Add the product info to data
    data = data + product_temp    
    print(f'Scrapped page {n}. Continue to page {n+1}')
        
    n += 1

    # Sleep the execution of script in random amount of time from 1 - 5 sec
    sleep_time = random.randint(1, 5)
    print(f'Scrapper sleep in {sleep_time}')
    sleep(sleep_time)

print(len(data))