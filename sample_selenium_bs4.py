import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

URL = "https://www.courts.ca.gov/opinions-slip.htm"
browser = webdriver.Chrome('/home/ruthraved/selenium-webdrivers/chromedriver')
browser.get(URL)
time.sleep(3)

html = browser.page_source
# print(html)
soup = BeautifulSoup(html, "lxml")

print(soup.find_all("iframe"))

browser.quit()