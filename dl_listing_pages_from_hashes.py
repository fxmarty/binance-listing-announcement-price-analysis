from bs4 import BeautifulSoup

import glob
import os
import sys

import requests

from config import project_path

from selenium import webdriver

filelist = glob.glob(os.path.join(project_path, 'pages/*.html'))

url = 'https://www.binance.com/en/support/announcement/62a72f3052674fc589ad401e973ce9ab'

page = requests.get(url)
data = page.text

soup = BeautifulSoup(data, 'html')

elements = soup.find_all("div", {"class": "css-17s7mnd"})

driver = webdriver.Firefox()

index = 1

base_url = 'https://www.binance.com/en/support/announcement/'

output_path = os.path.join(project_path, 'dat', 'annoucement_pages')

index = 1
with open(os.path.join(project_path, 'dat', 'page_hashes.txt'), 'r') as f:
    for line in f:
        line_stripped = line.rstrip()
        
        driver.get(os.path.join(base_url, line_stripped))
        
        index_formatted = str("{:03d}".format(index))
        
        with open(os.path.join(output_path, index_formatted + '.html'), 'w') as f_out:
            f_out.write(driver.page_source)
        
        index += 1
    
    driver.quit()