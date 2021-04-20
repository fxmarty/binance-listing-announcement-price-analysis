import time

from selenium import webdriver
from selenium.webdriver.common.by import By


class SaveHTML():
  def __init__(self, path):
    self.driver = webdriver.Firefox()
    
    self.index = 1
    
    self.path = path
    
    self.iterate()
    
  def go_through_page(self, nth_child_num, save_only=False, custom_selector=""):
    with open(self.path + 'page' + str(self.index) + '.html', 'w') as f:
        f.write(self.driver.page_source)
    
    if not save_only:
      if custom_selector == "":
        self.driver.find_element(By.CSS_SELECTOR,
                                ".mirror:nth-child("
                                  + str(nth_child_num)
                                  + ") > .css-ew2l8i"
                                ).click()
      else:
        self.driver.find_element(By.CSS_SELECTOR, custom_selector).click()
      self.index += 1
      time.sleep(1)  # this is extremely ugly, but works to wait for the load to finish

  def iterate(self):
    self.driver.get("https://www.binance.com/en/support/announcement/c-48")
    self.driver.set_window_size(1920, 989)
    
    # first pages are weird
    self.go_through_page(-1, custom_selector='.css-1tvfnbu > .css-ew2l8i')
    
    self.go_through_page(8)
    
    self.go_through_page(9)
    
    self.go_through_page(10)
    
    for i in range(42):
        self.go_through_page(11)
    
    self.go_through_page(10)
    
    self.go_through_page(9)
    
    self.go_through_page(8)
    
    self.go_through_page(-1, save_only=True)  # to save the last page
    
    self.driver.quit()

SaveHTML(path='/home/felix/Documents/Projets/binance-listing-announcement-price-analysis/pages/')