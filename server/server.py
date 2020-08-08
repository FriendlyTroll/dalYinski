#!/usr/bin/env python3

import socket
import time
import threading

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys

# local imports
from browser import FFBrowser


def get_ip_address():
    ''' gets the local ip address of pc where this server is running
    as socket.gethostname() returns a useless 127.0.0.1 '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

HOST = get_ip_address()
PORT = 65432
MAGIC = 'dalyinskimagicpkt'

def broadcastip():
    ''' Announcement service '''
    while True:
        sudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket
        sudp.bind(('', 0))
        sudp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # this is a broadcast socket
        data = MAGIC+HOST
        sudp.sendto(data.encode(), ('<broadcast>', PORT))
        print('Sent service announcement')
        time.sleep(5)

li = 0
def change_tab(webdrv):
    ''' Get current tab and loop through a list of tabs. Increment list index and try to get next tab
        and set that as current tab. Else end of list has been reached so reset
        the index to start of list i.e. first tab'''
    global li
    current_tab = webdrv.current_window_handle
    for handle in webdrv.window_handles:
        try:
            li += 1
            current_tab = webdrv.window_handles[li]
            return current_tab
        except IndexError:
            li = 0
            current_tab = webdrv.window_handles[li]
            return current_tab

### Main workhorse ###
def server_conn():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    
    while True:
       try:
            ''' Get new socket object from accept(). This is different from the listening socket above.
            This one is used to communicate with the client '''
            conn, addr = s.accept()
            print('Connected by', addr)
            data = conn.recv(1024).decode("utf-8")
            if "ping" in data:
                print('ping received')
            elif "fbro" in data:
                print('fbro received')
                # TODO: below copies the existing profile to /tmp and does so each time when run, maybe there is way to reuse it again? Or make the profile slimmer
                fp = webdriver.FirefoxProfile("/home/antisa/.mozilla/firefox/ne44ra9s.selenium")
                bro = webdriver.Firefox(fp)
                # TODO: add disable lazy loading of tabs for correct tab switching - set_preference()?
                bro.install_addon("/home/antisa/.mozilla/firefox/ne44ra9s.selenium/extensions/uBlock0@raymondhill.net.xpi")
                # bro.fullscreen_window()
                bro.get("https://www.youtube.com/")
            elif "playpause" in data:
                print('play/pause received')
                try:
                    bro.find_element_by_class_name("ytp-play-button").click()
                except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                    try:
                        # find "Play all" thumbnail then in "Watch later" playlist
                        bro.find_element_by_xpath("//img[@id='img'][@width='357']").click()
                    # no element at all
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                        print(e)
            elif "watchlater" in data:
                print('watchlater received')
                # Handle cases when finding elements doesn't work if the window is made smaller than half of screen beacuse only icons for navigation are then shown or just the hamburger icon is shown
                try:
                    # normal situation where elements are visible
                    bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() 
                except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
                    # hamburger only is visible
                    bro.find_element_by_xpath("//button[@id='button'][@aria-label='Guide']").click() # hamburger element
                    time.sleep(1) # wait a bit
                    bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() # Watch later element
            elif "playnext" in data:
                print('playnext received')
                try:
                    bro.find_element_by_class_name("ytp-next-button.ytp-button").click()
                except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                    print(e)
            elif "playprevious" in data:
                print('playprevious received')
                try:
                    bro.find_element_by_class_name("ytp-prev-button.ytp-button").click()
                except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                    print(e)
            elif "fullscreen" in data:
                print('fullscreen received')
                try:
                    bro.find_element_by_class_name("ytp-fullscreen-button.ytp-button").click()
                except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                    # mini player is opened, fullscreen it
                    try:
                        bro.find_element_by_class_name("ytp-miniplayer-expand-watch-page-button.ytp-button.ytp-miniplayer-button-top-left").click()
                    # no element at all
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                        print(e)
            elif "gohome" in data:
                print('gohome received')
                try:
                    bro.find_element_by_class_name("yt-simple-endpoint.style-scope.ytd-topbar-logo-renderer").click()
                except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                    print(e)
            elif "captions" in data:
                try:
                   bro.find_element_by_xpath("//button[@aria-label='Subtitles/closed captions (c)']").click()
                except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException) as e:
                    print(e)
            elif "switchtab" in data:
                print('switchtab received')
                print(bro.window_handles)
                next_tab = change_tab(bro)
                bro.switch_to.window(next_tab)
            elif not data:
                print('No data received')
            conn.sendall(b'Hi from server')

        # catch scenario where bro variable is not defined because user maybe clicked some other button before opening the webbrowser
       except UnboundLocalError as e:
           print(e)
    s.close()

# Spawn 2 threads, one for ip discovery other for server itself. The broadcasting thread is spawned as daemon because we don't want the main loop to wait for it to finish when exiting the program
bcast_t = threading.Thread(target=broadcastip, daemon=True)
main_t = threading.Thread(target=server_conn)

if __name__ == '__main__':
       # start the threads
       bcast_t.start()
       main_t.start()
