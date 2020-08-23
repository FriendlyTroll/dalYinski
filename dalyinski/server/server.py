#!/usr/bin/env python3

__version__ = '0.4'

import socket
import time
import threading
import os

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys

# local imports
from dalyinski.server.browser import FFBrowser

class ServerConn:
    def __init__(self):
        self.HOST = self.get_ip_address()
        self.PORT = 65432
        self.MAGIC = 'dalyinskimagicpkt'
        self.li = 0 # index used for change_tab()
    
    def browser_profile(self):
        ''' Find the selenium profile directory '''
        self.mozilla_dir = os.path.join(os.environ["HOME"], '.mozilla/firefox')
        for folder in os.listdir(self.mozilla_dir):
            if (folder.find("selenium") != -1):
                self.selenium_dir = folder
        self.mozilla_dir = os.path.join(self.mozilla_dir, self.selenium_dir)
        return self.mozilla_dir

    def get_ip_address(self):
        ''' Gets the local ip address of pc where this server is running
        as socket.gethostname() returns a useless 127.0.0.1 '''
        self.local_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local_s.connect(("8.8.8.8", 80))
        local_ip = self.local_s.getsockname()[0]
        self.local_s.close()
        return local_ip
    
    def broadcastip(self):
        ''' Announcement service. Sends UDP packets on network with MAGIC word + host ip. '''
        while True:
           sudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create udp socket
           sudp.bind(('', 0))
           sudp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # this is a broadcast socket
           data = self.MAGIC+self.HOST
           sudp.sendto(data.encode(), ('<broadcast>', self.PORT))
           print('Sent service announcement')
           time.sleep(5)
        print("[] broadcastip exited")
    
    def change_tab(self, webdrv):
        ''' Get current tab and loop through a list of tabs. Increment list index and try to get next tab
            and set that as current tab. Else end of list has been reached so reset
            the index to start of list i.e. first tab'''
        current_tab = webdrv.current_window_handle
        for handle in webdrv.window_handles:
            try:
                self.li += 1
                current_tab = webdrv.window_handles[self.li]
                return current_tab
            except IndexError:
                self.li = 0
                current_tab = webdrv.window_handles[self.li]
                return current_tab
    
    ### Main workhorse ###
    def server_conn(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen()
        
        while True:
           try:
               ''' Get new socket object from accept(). This is different from the listening socket above.
               This one is used to communicate with the client '''
               self.conn, self.addr = self.s.accept()
               print('Connected by', self.addr)
               self.data = self.conn.recv(1024).decode("utf-8")
               if "ping" in self.data:
                    print('ping received')
               elif "fbro" in self.data:
                    print('fbro received')
                    # TODO: below copies the existing profile to /tmp and does so each time when run, maybe there is way to reuse it again? Or make the profile slimmer
                    # self.fp = webdriver.FirefoxProfile("/home/antisa/.mozilla/firefox/ne44ra9s.selenium")
                    self.fp = webdriver.FirefoxProfile(self.browser_profile())
                    self.bro = webdriver.Firefox(self.fp)
                    # TODO: add disable lazy loading of tabs for correct tab switching - set_preference()?
                    # Install ublock origin if it exists
                    try:
                        self.ublock_ext = os.stat(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
                        if self.ublock_ext:
                            print("Installing uBlock Origin...")
                            self.bro.install_addon(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
                    except FileNotFoundError:
                        print("No uBlock Origin extension found")
                    # bro.fullscreen_window()
                    self.bro.get("https://www.youtube.com/")
               elif "playpause" in self.data:
                    print('play/pause received')
                    try:
                        self.bro.find_element_by_class_name("ytp-play-button").click()
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                        try:
                            # find "Play all" thumbnail then in "Watch later" playlist
                            self.bro.find_element_by_xpath("//img[@id='img'][@width='357']").click()
                        # no element at all
                        except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                            print(e)
                    try:
                        self.bro.find_element_by_xpath("//yt-button-renderer[@id='confirm-button']").click() # that annoying "Still watching?" popup
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                        print(e)
               elif "watchlater" in self.data:
                   print('watchlater received')
                   # Handle cases when finding elements doesn't work if the window is made smaller than half of screen beacuse only icons for navigation are then shown or just the hamburger icon is shown
                   try:
                       # normal situation where elements are visible
                       self.bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() 
                   except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
                       # hamburger only is visible
                       self.bro.find_element_by_xpath("//button[@id='button'][@aria-label='Guide']").click() # hamburger element
                       time.sleep(1) # wait a bit
                       self.bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() # Watch later element
               elif "playnext" in self.data:
                   print('playnext received')
                   try:
                       self.bro.find_element_by_class_name("ytp-next-button.ytp-button").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                       print(e)
               elif "playprevious" in self.data:
                   print('playprevious received')
                   try:
                       self.bro.find_element_by_class_name("ytp-prev-button.ytp-button").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                       print(e)
               elif "fullscreen" in self.data:
                   print('fullscreen received')
                   try:
                       self.bro.find_element_by_class_name("ytp-fullscreen-button.ytp-button").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                       # mini player is opened, fullscreen it
                       try:
                           self.bro.find_element_by_class_name("ytp-miniplayer-expand-watch-page-button.ytp-button.ytp-miniplayer-button-top-left").click()
                       # no element at all
                       except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                           print(e)
               elif "gohome" in self.data:
                   print('gohome received')
                   try:
                       self.bro.find_element_by_class_name("yt-simple-endpoint.style-scope.ytd-topbar-logo-renderer").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException) as e:
                       print(e)
               elif "captions" in self.data:
                   try:
                      self.bro.find_element_by_xpath("//button[@aria-label='Subtitles/closed captions (c)']").click()
                   except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException) as e:
                       print(e)
               elif "switchtab" in self.data:
                   print('switchtab received')
                   print(self.bro.window_handles)
                   next_tab = self.change_tab(self.bro)
                   self.bro.switch_to.window(next_tab)
               elif not self.data:
                   print('No data received')
               self.conn.sendall(b'Hi from server')
    
            # catch scenario where bro variable is not defined because user maybe clicked some other button before opening the webbrowser
           except UnboundLocalError as e:
               print(e)

           # TODO: clean up the socket on exit and/or Ctrl+C
        self.s.close()

    
    def run(self):
        ''' Spawn 2 threads, one for ip discovery other for server itself.
        Threads are spawned as daemon because we don't want the main loop to wait for them to 
        finish when exiting the program. Also, we are not .join()-ing the threads as that
        blocks the main thread.'''

        self.bcast_t = threading.Thread(target=self.broadcastip, daemon=True)
        self.main_t = threading.Thread(target=self.server_conn, daemon=True)
        self.bcast_t.start()
        self.main_t.start()
    


# BUG: below not working currently, as it exits immediately because both threads above are daemon
if __name__ == '__main__':
    srv = ServerConn()
    srv.run()
