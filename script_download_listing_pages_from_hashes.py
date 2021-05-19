import os
import glob
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from cfg.config import project_path

if __name__ == "__main__":

    # filelist = glob.glob(os.path.join(project_path, 'pages/*.html'))
    # url = 'https://www.binance.com/en/support/announcement/62a72f3052674fc589ad401e973ce9ab'
    # data = requests.get(url).text
    # soup = BeautifulSoup(data, 'html')
    # elements = soup.find_all("div", {"class": "css-17s7mnd"})
    # index = 1

    driver = webdriver.Firefox()

    base_url = "https://www.binance.com/en/support/announcement/"
    output_path = os.path.join(project_path, "dat", "annoucement_pages")

    with open(os.path.join(project_path, "dat", "page_hashes.txt"), "r") as f:
        for index, line in enumerate(f):
            line_stripped = line.rstrip()
            driver.get(os.path.join(base_url, line_stripped))
            index_formatted = str("{:03d}".format(index + 1))
            with open(os.path.join(output_path, index_formatted + ".html"), "w") as f_out:
                f_out.write(driver.page_source)

        driver.quit()
