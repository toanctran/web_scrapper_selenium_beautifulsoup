from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import time, sleep
DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'


options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://vnexpress.net/")
# content = driver.page_source()


SCROLL_PAUSE_TIME = 0.5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        content = driver.find_element_by_class_name('footer').get_attribute('innerHTML')
        break
    last_height = new_height



driver.quit()

from bs4 import BeautifulSoup

soup = BeautifulSoup(content, 'html.parser')


item_menu = soup.find_all('li', {'class': 'item-menu'})
data = {}
for item in item_menu:
    item_name = item.a.text
    item_link = item.a['href']
    data[item_name] = item_link

print(data)