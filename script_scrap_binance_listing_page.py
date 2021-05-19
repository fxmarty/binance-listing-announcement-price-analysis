import os
import time
from selenium import webdriver
from cfg.config import project_path
from selenium.webdriver.common.by import By


class SaveHTML():
    def __init__(self, path):
        self.driver = webdriver.Firefox()
        self.index = 1
        self.path = path
        self.iterate()

    def go_through_page(self, nth_child_num, save_only=False, custom_selector=""):
        """
        This function formats the index as "01", "02", ..., "50" for nice ordering
        """

        with open(self.path + 'page' + str("{:02d}".format(self.index)) + '.html', 'w') as f:
            f.write(self.driver.page_source)

        if not save_only:
            if custom_selector == "":
                element_css = ".mirror:nth-child(" + str(nth_child_num) + ") > .css-ew2l8i"
                self.driver.find_element_by_css_selector(element_css).click()
            else:
                self.driver.find_element_by_css_selector(custom_selector).click()
            self.index += 1

            # This is extremely ugly, but works to wait for the load to finish
            time.sleep(1)

    def iterate(self):
        self.driver.get("https://www.binance.com/en/support/announcement/c-48")
        self.driver.set_window_size(1920, 989)

        # First pages are weird
        self.go_through_page(-1, custom_selector='.css-1tvfnbu > .css-ew2l8i')
        self.go_through_page(8)
        self.go_through_page(9)
        self.go_through_page(10)

        for _ in range(43):
            self.go_through_page(11)

        self.go_through_page(10)
        self.go_through_page(9)
        self.go_through_page(8)
        self.go_through_page(-1, save_only=True)  # to save the last page
        self.driver.quit()


if __name__ == "__main__":
    SaveHTML(path=os.path.join(project_path, 'dat', 'pages/'))