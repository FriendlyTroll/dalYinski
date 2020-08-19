#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class FFBrowser:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        self.driver.get(url)

if __name__ == '__main__':
    bro = FFBrowser("https://python.org")
