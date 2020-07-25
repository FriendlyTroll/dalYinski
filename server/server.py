#!/usr/bin/env python3

import socket
import time

from selenium import webdriver
from selenium.common import exceptions

# local imports
from .browser import FFBrowser

HOST = '0.0.0.0'
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

def main():
    while True:
        # Get new socket object from accept(). This is different from the listening socket above.
        # This one is used to communicate with the client
        conn, addr = s.accept()
        print('Connected by', addr)
        data = conn.recv(1024).decode("utf-8")
        if "ping" in data:
            print('ping received')
        elif "fbro" in data:
            print('fbro received')
            # TODO: below copies the existing profile to /tmp and does so each time when run, maybe there is way to reuse it again? Or make the profile slimmer
            fp = webdriver.FirefoxProfile("/home/antisa/.mozilla/firefox/ne44ra9s.selenium/")
            bro = webdriver.Firefox(fp)
            bro.install_addon("/home/antisa/Downloads/ublock_origin-1.28.2-an+fx.xpi")
            bro.get("https://www.youtube.com/")
            # BUG: playpause not working when there is a mini player
        elif "playpause" in data:
            print('play/pause received')
            try:
                bro.find_element_by_class_name("ytp-play-button").click()
            except exceptions.NoSuchElementException as e:
                # find "Play all" thumbnail then in "Watch later" playlist
                bro.find_element_by_xpath("//img[@id='img'][@width='357']").click()
        elif "watchlater" in data:
            print('watchlater received')
            # Handle cases when finding elements doesn't work if the window is made smaller than half of screen beacuse only icons for navigation are then shown or just the hamburger icon is shown
            try:
                # normal situation where elements are visible
                bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@title='Watch later']").click()
            except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
                # hamburger only is visible
                bro.find_element_by_xpath("//button[@id='button'][@aria-label='Guide']").click() # hamburger element
                time.sleep(1) # wait a bit
                bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@title='Watch later']").click() # Watch later element
        elif "playnext" in data:
            print('playnext received')
            bro.find_element_by_class_name("ytp-next-button.ytp-button").click()
        elif "fullscreen" in data:
            print('fullscreen received')
            try:
                bro.find_element_by_class_name("ytp-fullscreen-button.ytp-button").click()
            except exceptions.ElementNotInteractableException as e:
                # mini player is opened, fullscreen it
                bro.find_element_by_class_name("ytp-miniplayer-expand-watch-page-button.ytp-button.ytp-miniplayer-button-top-left").click()
        elif "gohome" in data:
            print('gohome received')
            try:
                bro.find_element_by_class_name("yt-simple-endpoint.style-scope.ytd-topbar-logo-renderer").click()
            except exceptions.ElementNotInteractableException as e:
                # TODO: add functionality
                pass
        elif not data:
            print('No data received')
        conn.sendall(b'Hi from server')
    s.close()

if __name__ == '__main__':
    main()
