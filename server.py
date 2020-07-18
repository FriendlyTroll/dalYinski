#!/usr/bin/env python3

import socket
from selenium import webdriver
from selenium.common import exceptions
import time

# local imports
from browser import FFBrowser

HOST = '0.0.0.0'
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

    # Get new socket object from accept(). This is different from the listening socket above.
    # This one is used to communicate with the client
while True:
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
            # find "Play all" thumbnail then
            bro.find_element_by_xpath("//img[@id='img'][@width='357']").click()
    elif "watchlater" in data:
        print('watchlater received')
        # BUG: finding elements by link text doesn't work if the window is made smaller than half of screen beacuse only icons for navigation are then shown
        bro.find_element_by_link_text("Watch later").click()
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
        # BUG: doesn't work from fullscreen video -> selenium.common.exceptions.ElementNotInteractableException: Message: Element <a id="logo" class="yt-simple-endpoint style-scope ytd-topbar-logo-renderer" href="/"> could not be scrolled into view
        print('gohome received')
        bro.find_element_by_class_name("yt-simple-endpoint.style-scope.ytd-topbar-logo-renderer").click()
    elif not data:
        print('No data received')
    conn.sendall(b'Hi from server')
s.close()
