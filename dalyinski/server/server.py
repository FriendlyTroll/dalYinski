#!/usr/bin/env python3

# BUG: Message: Browsing context has been discarded, when you switch tabs then return to youtube
# BUG: Handle clicking immediately on fullscreen button
# BUG: If the browser is minimized nothing gets sent to client
__version__ = 0.16

import socket
import time
import threading
import os
import pickle
import struct
import sys
import urllib.request
import zipfile

# hide geckodriver console on Windows
if os.name == 'nt':
    import win32gui

    def enumWindowFunc(hwnd, windowList):
        """ win32gui.EnumWindows() callback """
        text = win32gui.GetWindowText(hwnd)
        className = win32gui.GetClassName(hwnd)
        if 'geckodriver' in text.lower() or 'geckodriver' in className.lower():
            win32gui.ShowWindow(hwnd, False)

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# local imports
from dalyinski.server.browser import FFBrowser
from dalyinski.server.gui_dialogs import InfoFrame

class ServerConn:
    def __init__(self):
        print(f'Server version: {__version__}')
        self.HOST = self.get_ip_address()
        self.PORT = 65432
        self.MAGIC = 'dalyinskimagicpkt'
        self.li = 0 # index used for change_tab()
    
    def browser_profile(self):
        ''' Find the selenium profile directory. Check if we are
        on Linux (posix) or Windows (nt).'''
        if os.name == 'posix':
            self.mozilla_dir = os.path.join(os.environ["HOME"], '.mozilla/firefox')
            for folder in os.listdir(self.mozilla_dir):
                if (folder.find("selenium") != -1):
                    self.selenium_dir = folder
            if not self.selenium_dir:
                info = InfoFrame(text="Looks like you didn't create separate Firefox profile.\n Please create it first.")
                info.Show()
                sys.exit()
            self.mozilla_dir = os.path.join(self.mozilla_dir, self.selenium_dir)
            return self.mozilla_dir
        elif os.name == 'nt':
            m = "Mozilla"
            f = "Firefox"
            p = "Profiles"
            # %APPDATA% is usually C:\Users\<Username>\AppData\Roaming; escape backslash
            self.mozilla_dir = os.path.join(os.environ["APPDATA"], m, f, p + '\\')
            for folder in os.listdir(self.mozilla_dir):
                if (folder.find("selenium") != -1):
                    self.selenium_dir = folder
            if not self.selenium_dir:
                info = InfoFrame(text="Looks like you didn't create separate Firefox profile.\n Please create it first.")
                info.Show()
                sys.exit()
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
           time.sleep(3)
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

    def dl_windows_geckodriver(self):
        ''' Download the windows geckodriver and move it into PATH.
        Linux geckodriver is installed when the server package is installed. '''
        gd_zip = os.path.join(os.environ["TMP"], 'geckodriver.zip')
        gd = os.environ["USERPROFILE"]
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-win64.zip'
        if not os.path.isfile(os.path.join(gd, 'geckodriver.exe')):
            print("Downloading geckodriver binary...")
            urllib.request.urlretrieve(url, gd_zip)
            with zipfile.ZipFile(gd_zip) as zipf:
                print("Extracting file...")
                zipf.extractall(gd)
        else:
            pass

    def dl_ublock(self):
        ''' Download ublock extension. '''
        url = 'https://addons.mozilla.org/firefox/downloads/file/3701081/ublock_origin-1.32.4-an+fx.xpi'

        # make sure extensions directory exists
        ext_dir = os.path.join(self.browser_profile(), "extensions")
        if not os.path.isdir(ext_dir):
            os.mkdir(ext_dir)

        ubf = self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi"
        if not os.path.isfile(ubf):
            urllib.request.urlretrieve(url, ubf)

    def check_new_version(self):
        ''' Check for new server version by comparing string in text files. '''
        try:
            if os.name == 'posix':
                v = urllib.request.urlopen('https://friendlytroll.github.io/dalYinski/LINUX_SERVER_VERSION.txt')
            elif os.name == 'nt':
                v = urllib.request.urlopen('https://friendlytroll.github.io/dalYinski/WIN_SERVER_VERSION.txt')

            ver = v.read(10).decode('utf-8') # read 10 bytes from response and decode
            if __version__ < float(ver): # if this file has smaller version number than the one entered in text file, show info
                print("New server version is available!")
                info = InfoFrame(text="New server version is available!\nDownload it from https://friendlytroll.github.io/dalYinski")
                info.Show()
        except Exception as e:
            print("Exception when checking for new version: ", type(e), e)

    def open_browser(self):
        ''' Open browser, load profile and install uBlock origin. '''
        '''
        # TODO: below copies the existing profile to /tmp and does so each time when run, maybe there is way to reuse it again? Or make the profile slimmer
        /usr/bin/firefox" "--marionette" "-foreground" "-no-remote" "-profile" "/tmp/rust_mozprofile3YPy06" is the command used to run it, try changing the -profile
        argument to point to profile where its copied from.
        '''
        if os.name == 'nt':
            self.dl_windows_geckodriver()
        f_profile = webdriver.FirefoxProfile(self.browser_profile())
        if os.name == 'posix':
            log_path = '/tmp/geckodriver.log'
            self.bro = webdriver.Firefox(firefox_profile=f_profile, service_log_path=log_path)
            self.check_new_version()
        elif os.name == 'nt':
            # TMP = C:\Users\ante\AppData\Local\Temp
            log_path = os.path.join(os.environ["TMP"], 'geckodriver.log')
            self.bro = webdriver.Firefox(firefox_profile=f_profile, service_log_path=log_path, executable_path=os.path.join(os.environ["USERPROFILE"], "geckodriver.exe"))
            win32gui.EnumWindows(enumWindowFunc, []) # close geckodriver console window
            self.check_new_version()
        if os.name == 'posix':
            try:
                self.ublock_ext = os.stat(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
                if self.ublock_ext:
                    print("Found existing uBlock Origin. Installing now...")
                    self.bro.install_addon(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
            except FileNotFoundError:
                print("No uBlock Origin extension found. Downloading...")
                self.dl_ublock()
                self.ublock_ext = os.stat(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
                if self.ublock_ext:
                    print("Installing uBlock Origin...")
                    self.bro.install_addon(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
        elif os.name == 'nt':
            try:
                self.ublock_ext = os.stat(self.browser_profile() + r"\extensions\uBlock0@raymondhill.net.xpi")
                if self.ublock_ext:
                    print("Found existing uBlock Origin. Installing now...")
                    self.bro.install_addon(self.browser_profile() + r"\extensions\uBlock0@raymondhill.net.xpi")
            except FileNotFoundError:
                print("No uBlock Origin extension found. Downloading...")
                self.dl_ublock()
                self.ublock_ext = os.stat(self.browser_profile() + r"\extensions\uBlock0@raymondhill.net.xpi")
                if self.ublock_ext:
                    print("Installing uBlock Origin...")
                    self.bro.install_addon(self.browser_profile() + r"\extensions\uBlock0@raymondhill.net.xpi")

        # self.bro.fullscreen_window()
        self.bro.get("https://www.youtube.com/")

    def close_browser(self):
        try:
            self.bro.quit()
        except Exception as e:
            print("Error when trying to quit browser")

    ### Main workhorse ###
    def server_conn(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen()
        
        while True:
           try:
               ''' Get new socket object from accept(). This is different from the listening socket above.
               This one is used to communicate with the client '''
               self.conn, self.addr = self.s.accept()
               print('Connected by', self.addr)
               self.data = self.conn.recv(1024).decode("utf-8")
               if "fbro" in self.data:
                    print('fbro received')
                    self.open_browser()
               elif "ping" in self.data:
                   print("ping received")
               elif "playpause" in self.data:
                    print('play/pause received')
                    try:
                        # find "Play all" thumbnail then in "Watch later" playlist
                        self.bro.find_element_by_xpath("//img[@id='img'][@width='357']").click()
                        print("WATCH LATER play")
                    # no element at all
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                        print(e)
                    try:
                        self.bro.find_element_by_xpath("//yt-formatted-string[@id='text']").click() # that annoying "Still watching?" popup
                        print("STILL WATCHING play")
                    except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                        print(e)
                        try:
                        # TODO: k BUTTON exception:  Message: (539, -175) is out of bounds of viewport width (1090) and height (807)
                            ActionChains(self.bro).send_keys_to_element(self.bro.find_element_by_tag_name('body'), 'k').perform()
                            print("k BUTTON play")
                        except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException,exceptions.TimeoutException, exceptions.MoveTargetOutOfBoundsException, exceptions.WebDriverException, exceptions.InvalidSessionIdException) as e:
                            print("k BUTTON exception: ", e)
               elif "watchlater" in self.data:
                   print('watchlater received')
                   # Handle cases when finding elements doesn't work if the window is made smaller than half of screen beacuse only icons for navigation are then shown or just the hamburger icon is shown
                   try:
                       # normal situation where elements are visible
                       self.bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() 
                   except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       try:
                           # hamburger only is visible
                           self.bro.find_element_by_xpath("//yt-icon-button[@id='guide-button'][@class='style-scope ytd-masthead']").click() # hamburger element
                           time.sleep(1) # wait a bit
                           self.bro.find_element_by_xpath("//a[@id='endpoint'][@role='tablist'][@href='/playlist?list=WL']").click() # Watch later element
                       except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                           print("watchlater exception caught: ", e)
               elif "playnext" in self.data:
                   print('playnext received')
                   try:
                       ActionChains(self.bro).key_down(Keys.LEFT_SHIFT).send_keys('n').key_up(Keys.LEFT_SHIFT).perform()
                   except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.InvalidSessionIdException) as e:
                       print(e)
               elif "playprevious" in self.data:
                   print('playprevious received')
                   try:
                       ActionChains(self.bro).key_down(Keys.LEFT_SHIFT).send_keys('p').key_up(Keys.LEFT_SHIFT).perform()
                   except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException, exceptions.InvalidSessionIdException) as e:
                       print(e)
               elif "fullscreen" in self.data:
                   print('fullscreen received')
                   try:
                       self.bro.find_element_by_class_name("ytp-fullscreen-button.ytp-button").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       try:
                           # mini player is opened, fullscreen it
                           self.bro.find_element_by_class_name("ytp-miniplayer-expand-watch-page-button.ytp-button.ytp-miniplayer-button-top-left").click()
                       # no element at all
                       except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                           print(e)
               elif "gohome" in self.data:
                   print('gohome received')
                   try:
                       self.bro.find_element_by_class_name("yt-simple-endpoint.style-scope.ytd-topbar-logo-renderer").click()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       self.bro.get("https://www.youtube.com/")
                       print(type(e), e)
               elif "captions" in self.data:
                   print("captions received")
                   try:
                      self.bro.find_element_by_xpath("//button[@class='ytp-subtitles-button ytp-button']").click()
                   except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       print("captions exception: ", e)
               elif "switchtab" in self.data:
                   print('switchtab received')
                   try:
                       print(self.bro.window_handles)
                       next_tab = self.change_tab(self.bro)
                       self.bro.switch_to.window(next_tab)
                   except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       print("switchtab exception: ", e)
               elif "fforward" in self.data:
                   print('fforward received')
                   try:
                       ActionChains(self.bro).send_keys_to_element(self.bro.find_element_by_tag_name('body'), Keys.ARROW_RIGHT).perform()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       print(e)
               elif "rewind" in self.data:
                   print('rewind received')
                   try:
                       ActionChains(self.bro).send_keys_to_element(self.bro.find_element_by_tag_name('body'), Keys.ARROW_LEFT).perform()
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       print(e)
               elif "getthumbnails" in self.data:
                   print("getthumbnails received")
                   try:
                       try:
                           time.sleep(1.0)
                           for _ in range(3):
                               # scroll the page so that JS loads some videos to send
                               self.bro.execute_script(self.js_scroll_down(3000))
                               time.sleep(1.0)
                       except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                           print(type(e), e)

                       # stuff we're going to send to client
                       elem_img = self.bro.find_elements_by_xpath('//ytd-thumbnail[@class="style-scope ytd-rich-grid-media"]/a[@id="thumbnail"]/yt-img-shadow/img[@id="img"]')
                       elem_txt_href = self.bro.find_elements_by_xpath('//div[@id="details"]/div[@id="meta"]/h3/a[@id="video-title-link"]')

                       # print(f"### {elem_img}")
                       # print(f"$$$ {elem_txt_href}")
                       self.zip_lists(elem_img, elem_txt_href)
                       try:
                           # scroll back to top of page
                           self.bro.execute_script(self.js_scroll_up(9000))
                       except exceptions.JavascriptException as e:
                           print(e)
                   except (exceptions.ElementNotInteractableException,exceptions.NoSuchElementException, exceptions.InvalidSessionIdException, exceptions.WebDriverException) as e:
                       print("getthumbnails exception: ", e)
                       self.conn.sendall(b"!! getthumbnails errored out!")
               elif "getplaylistthumbnails" in self.data:
                   print("getplaylistthumbnails received")
                   try:
                       # wait for stuff to load
                       time.sleep(1)
                       # Get document height so that we scroll certain amount of times for the videos to load
                       document_height = self.bro.execute_script('return document.documentElement.scrollHeight')
                       scroll_amount = int(document_height/1000) + 1
                       for _ in range(scroll_amount):
                               time.sleep(0.8)
                               self.bro.execute_script(self.js_scroll_down(1000))

                       # BUG: when there's private video, there's no image for it so the thumbnail images after those video don't match description
                       elem_img = self.bro.find_elements_by_xpath('//ytd-thumbnail[@id="thumbnail"][@class="style-scope ytd-playlist-video-renderer"]/a[@id="thumbnail"]/yt-img-shadow/img[@id="img"]')
                       elem_href = self.bro.find_elements_by_xpath('//a[@class="yt-simple-endpoint style-scope ytd-playlist-video-renderer"]')
                       elem_vid_desc = self.bro.find_elements_by_xpath('//div[@id="meta"][@class="style-scope ytd-playlist-video-renderer"]/h3/span[@id="video-title"]')

                       # if one of the lists are empty, try to find new elements (necessary for example when browsing history)
                       if not(elem_img or elem_href or elem_vid_desc):
                           elem_img = self.bro.find_elements_by_xpath('//ytd-thumbnail[@class="style-scope ytd-video-renderer"]/a[@id="thumbnail"]/yt-img-shadow/img[@id="img"]')
                           elem_href = self.bro.find_elements_by_xpath('//a[@id="thumbnail"][@class="yt-simple-endpoint inline-block style-scope ytd-thumbnail"]')
                           elem_vid_desc = self.bro.find_elements_by_xpath('//div[@id="meta"][@class="style-scope ytd-video-renderer"]/div[@id="title-wrapper"]/h3/a[@id="video-title"]')

                       self.zip_lists(elem_img, elem_href, plst_vid_desc=elem_vid_desc)
                   except Exception as e:
                       print("getplaylistthumbnails exception: ", type(e), e)
                       self.conn.sendall(b"!! getplaylistthumbnails errored out!")
               elif "getsubscriptionhumbnails" in self.data:
                   print("getsubscriptionhumbnails received")
                   try:
                       # wait for stuff to load
                       time.sleep(1)
                       # Get document height so that we scroll certain amount of times for the videos to load
                       document_height = self.bro.execute_script('return document.documentElement.scrollHeight')
                       scroll_amount = int(document_height/1000) + 1
                       for _ in range(scroll_amount):
                               time.sleep(0.8)
                               self.bro.execute_script(self.js_scroll_down(1000))

                       elem_img = self.bro.find_elements_by_xpath('//ytd-thumbnail[@class="style-scope ytd-grid-video-renderer"]/a[@id="thumbnail"]/yt-img-shadow/img[@id="img"]')
                       elem_href = self.bro.find_elements_by_xpath('//ytd-thumbnail[@class="style-scope ytd-grid-video-renderer"]/a[@id="thumbnail"][@class="yt-simple-endpoint inline-block style-scope ytd-thumbnail"]')
                       elem_vid_desc = self.bro.find_elements_by_xpath('//div[@id="meta"][@class="style-scope ytd-grid-video-renderer"]/h3/a[@id="video-title"][@class="yt-simple-endpoint style-scope ytd-grid-video-renderer"]')

                       # print("EL ###", elem_img)
                       # print("EHREF ###", elem_href)
                       # print("EVIDDESC ###", elem_vid_desc)
                       self.zip_lists(elem_img, elem_href, plst_vid_desc=elem_vid_desc)
                   except Exception as e:
                       print("getsubscriptionhumbnails exception: ", type(e), e)
                       self.conn.sendall(b"!! getsubscriptionhumbnails errored out!")
               elif "getplaylists" in self.data:
                   print("getplaylists received")
                   try:
                       try:
                           # expand "Show more" first
                           self.bro.find_element_by_xpath('//ytd-guide-entry-renderer[@id="expander-item"]/a[@id="endpoint"]/paper-item/yt-icon[@class="guide-icon style-scope ytd-guide-entry-renderer"]').click()
                       except (exceptions.ElementNotInteractableException, exceptions.NoSuchElementException) as e:
                           try:
                               print("Show more exception: ", type(e), e)
                               # Open hamburger menu and locate the element
                               self.bro.find_element_by_xpath('//yt-icon[@id="guide-icon"][@class="style-scope ytd-masthead"][@icon="yt-icons:menu"]').click()
                               time.sleep(1) # wait a bit
                               self.bro.find_element_by_xpath('//ytd-guide-entry-renderer[@id="expander-item"]/a[@id="endpoint"]/paper-item/yt-icon[@class="guide-icon style-scope ytd-guide-entry-renderer"]').click()
                           except (exceptions.ElementNotInteractableException, exceptions.ElementClickInterceptedException) as e:
                               print("The list of playlists is probably already expanded. Got exception: ", type(e), e)
                               # simply move on to getting the videos below
                               pass

                       # Your videos, Your movies and Watch later elements
                       vid_mv_wl = self.bro.find_elements_by_xpath('//div[@id="section-items"]/ytd-guide-entry-renderer/a[@id="endpoint"][@class="yt-simple-endpoint style-scope ytd-guide-entry-renderer"]')
                       # Rest of collapsible elements where user playlists are
                       collaps_entries = self.bro.find_elements_by_xpath('//ytd-guide-collapsible-entry-renderer/div[@id="expanded"]/div[@id="expandable-items"]/ytd-guide-entry-renderer/a[@id="endpoint"][@class="yt-simple-endpoint style-scope ytd-guide-entry-renderer"]')

                       usr_playlists = [] # combo of above 2 lists, a list of tuples of playlist name and link
                       for el in vid_mv_wl:
                           try:
                               usr_playlists.append((el.get_attribute("title"), el.get_attribute("href")))
                           except Exception as e:
                               print("vid_mv_wl EXCEPTION: ", e)

                       for el in collaps_entries:
                           try:
                               usr_playlists.append((el.get_attribute("title"), el.get_attribute("href")))
                           except Exception as e:
                               print("collaps_entries EXCEPTION: ", e)

                       msg = pickle.dumps(usr_playlists)
                       print("Pickled msg lenght is: ", len(msg))
                       self.send_url_list(self.conn, msg)
                       print("DATA SENT!!!...")
                   except Exception as e:
                       print("getplaylists exception: ", type(e), e)
                       self.conn.sendall(b"!! getplaylists errored out!")
               elif "playvideo" in self.data:
                   print("playvideo received")
                   try:
                       # self.data.split()[1] is video url received from client
                       self.bro.get(self.data.split()[1])
                   except Exception as e:
                       print("playvideo EXCEPTION: ", e)

               elif "subscriptions" in self.data:
                   print("subscriptions received")
                   try:
                      self.bro.find_element_by_xpath("//a[@id='endpoint'][@href='/feed/subscriptions']/paper-item/yt-icon").click()
                   except Exception as e:
                       print("subscriptions EXCEPTION: ", type(e), e)
                       # Open hamburger menu and locate the element
                       self.bro.find_element_by_xpath('//yt-icon[@id="guide-icon"][@class="style-scope ytd-masthead"][@icon="yt-icons:menu"]').click()
                       time.sleep(1) # wait a bit
                       self.bro.find_element_by_xpath("//a[@id='endpoint'][@href='/feed/subscriptions']/paper-item/yt-icon").click()
               elif "volup" in self.data:
                   print("volup received")
                   try:
                       ActionChains(self.bro).send_keys_to_element(self.bro.find_element_by_xpath('//div[@class="ytp-left-controls"]'), Keys.ARROW_UP).perform()
                   except Exception as e:
                       print("volup EXCEPTION: ", e)
               elif "voldown" in self.data:
                   print("voldown received")
                   try:
                       ActionChains(self.bro).send_keys_to_element(self.bro.find_element_by_xpath('//div[@class="ytp-left-controls"]'), Keys.ARROW_DOWN).perform()
                   except Exception as e:
                       print("voldown EXCEPTION: ", e)
               elif not self.data:
                   print('No data received')
               self.conn.sendall(b'Hi from server')
    
            # catch scenario where bro variable is not defined because user maybe clicked some other button before opening the webbrowser
           except (UnboundLocalError, AttributeError) as e:
               print("Caught error: ", e)
               self.conn.sendall(b'Server caught error.')
        self.s.close()

    def send_url_list(self, sock, data):
        ''' Adapted from here
        https://stackoverflow.com/questions/42459499/what-is-the-proper-way-of-sending-a-large-amount-of-data-over-sockets-in-python

        Get total length of data in bytes to send and send that as first 
        4 bytes to the client (check python struct docs). Then send all of the message which the
        client will read in 4096 byte chunks. See android/client.py.
        ''' 
        length = struct.pack('!I', len(data))
        sock.sendall(length)
        sock.sendall(data)
    
    def zip_lists(self, elem_img, elem_txt_href, plst_vid_desc=None):
        ''' Take in 2 lists, one with images one with descriptions
        and zip them up and send over socket. '''
        thumbs2send = [] # image list
        for el in elem_img:
            try:
                if el.get_attribute("src").startswith("https://i.ytimg.com/vi"):
                   thumbs2send.append(el.get_attribute("src"))
            except Exception as e:
                print("thumbs2send EXCEPTION: ", type(e), e)
        # print("Thumbs: ", thumbs2send)

        if plst_vid_desc:
            text2send = []
            for txt in plst_vid_desc:
                try:
                    if txt.get_attribute("title"):
                        text2send.append(txt.get_attribute("title"))
                except Exception as e:
                    print("text2send EXCEPTION: ", type(e), e)
            # print("Vid desc: ", text2send)
        else:
            text2send = [] # video description
            for txt in elem_txt_href:
                try:
                    if txt.get_attribute("title"):
                        text2send.append(txt.get_attribute("title"))
                except Exception as e:
                    print("text2send EXCEPTION: ", type(e), e)
            # print("Vid desc: ", text2send)

        href2send = [] # video links
        for lnk in elem_txt_href:
            try:
                href2send.append(lnk.get_attribute("href"))
            except Exception as e:
                print("href2send EXCEPTION: ", type(e), e)
        # print("Links  ", href2send)

        thumbnail_info = zip(text2send, thumbs2send, href2send)
        thumbnail_info_l = list(thumbnail_info)
        msg = pickle.dumps(thumbnail_info_l)
        print("Pickled msg lenght is: ", len(msg))
        self.send_url_list(self.conn, msg)
        print("DATA SENT!!!...")

    def js_scroll_down(self, n_pixels):
        '''Scroll down using javascript by n_pixels. Double curvy brackets are
        needed for the .format method to work correctly. '''
        return '''window.scrollBy({{ top: {px}, behavior: 'smooth'}});'''.format(px=n_pixels)
    
    def js_scroll_up(self, n_pixels):
        return '''window.scrollBy({{ top: -{px}, behavior: 'smooth'}}); '''.format(px=n_pixels)

    def run(self):
        ''' Spawn 2 threads, one for ip discovery other for server itself.
        Threads are spawned as daemon because we don't want the main loop to wait for them to 
        finish when exiting the program. Also, we are not .join()-ing the threads as that
        blocks the main thread.
        '''

        self.bcast_t = threading.Thread(target=self.broadcastip, daemon=True)
        self.main_t = threading.Thread(target=self.server_conn, daemon=True)
        self.bcast_t.start()
        self.main_t.start()
    


# BUG: below not working currently, as it exits immediately because both threads above are daemon
if __name__ == '__main__':
    srv = ServerConn()
    srv.run()
