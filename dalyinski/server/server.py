#!/usr/bin/env python3

# BUG: Message: Browsing context has been discarded, when you switch tabs then return to youtube
# BUG: Handle clicking immediately on fullscreen button

__version__ = '0.9'

import socket
import time
import threading
import os
import pickle
import struct

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from gi.repository import Gtk, Notify

# local imports
from dalyinski.server.browser import FFBrowser

class ServerConn:
    def __init__(self):
        print(f'Server version: {__version__}')
        self.HOST = self.get_ip_address()
        self.PORT = 65432
        self.MAGIC = 'dalyinskimagicpkt'
        self.li = 0 # index used for change_tab()
        self.last_thumbnail_was = '' # keep track of the last thumbnail command; see below
    
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
    
    def open_browser(self):
        ''' Open browser and load profile and install uBlock origin if it exists '''
        # TODO: below copies the existing profile to /tmp and does so each time when run, maybe there is way to reuse it again? Or make the profile slimmer
        self.fp = webdriver.FirefoxProfile(self.browser_profile())
        Notify.init('dalYinski server')
        noticon = Notify.Notification.new('dalYinski server', 'Opening web browser', '/usr/share/pixmaps/dalyinski-server.png')
        noticon.show()
        self.bro = webdriver.Firefox(self.fp)
        try:
            self.ublock_ext = os.stat(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
            if self.ublock_ext:
                print("Installing uBlock Origin...")
                self.bro.install_addon(self.browser_profile() + "/extensions/uBlock0@raymondhill.net.xpi")
        except FileNotFoundError:
            print("No uBlock Origin extension found")
        # bro.fullscreen_window()
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
               elif "selectthumb" in self.data:
                    try:
                        # Try clicking on selected video on Home page. Keep track of what was the last command received for
                        # the thumbnail so that we can click on the correct one. We need index - 1 because it is immediately
                        # incremented in the nextthumb handler below, after drawing the border
                        print("Javascript PLAYPAUSE")
                        if self.last_thumbnail_was == 'prevthumb':
                            self.bro.execute_script('''
var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
thumbnailList[window.current_idx].click();
                        ''')
                        else:
                            self.bro.execute_script('''
var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
thumbnailList[window.current_idx - 1].click();
                        ''')
                    except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                       print("Javascript Exception >>", e)
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
                           self.bro.find_element_by_xpath("//button[@id='button'][@aria-label='Guide']").click() # hamburger element
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
                       # mini player is opened, fullscreen it
                       try:
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
                      self.bro.find_element_by_xpath("//button[@aria-label='Subtitles/closed captions (c)']").click()
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
               elif "nextthumb" in self.data:
                   print('nextthumb received')
                   try:
                       if self.last_thumbnail_was == 'prevthumb':
                           self.bro.execute_script('''
/* 
Defining a variable current_idx as "var current_idx = 0" limits the scope to the
execution of the script. Selenium wraps the execution of javascript snippets into
their own script so variables don't survive the end of the script (if..else always
sees current_idx = 0). window.current_idx puts the variable into global scope
*/
if (typeof window.current_idx === 'undefined') {
	window.current_idx = 0;  
  
}

var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
if (current_idx == 0) {
    thumbnailList[window.current_idx].style.setProperty('border', '8px inset red'); // set border on current thumbnail
    window.current_idx +=1;
} else {
    window.current_idx +=1; // since last command was prevthumb we need to increment the index first for drawing the border
    thumbnailList[window.current_idx - 1].style.removeProperty('border'); // remove border from previous thumbnail
    thumbnailList[window.current_idx].style.setProperty('border', '8px inset red'); // set border on current thumbnail
    window.current_idx +=1; // increment index again to get next thumbnail
} ''')
                           self.last_thumbnail_was = 'nextthumb'
                       else:
                           self.bro.execute_script('''
if (typeof window.current_idx === 'undefined') {
	window.current_idx = 0;  
  
}

var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
if (current_idx == 0) {
    thumbnailList[window.current_idx].style.setProperty('border', '8px inset red'); // set border on current thumbnail
    window.current_idx +=1;
} else {
    thumbnailList[window.current_idx - 1].style.removeProperty('border'); // remove border from previous thumbnail
    thumbnailList[window.current_idx].style.setProperty('border', '8px inset red'); // set border on current thumbnail
    window.current_idx +=1;
} ''')
                           self.last_thumbnail_was = 'nextthumb'
                   except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                       print(e)
               elif "prevthumb" in self.data:
                  print('prevthumb received') 
                  try:
                      if self.last_thumbnail_was == 'nextthumb':
                          self.bro.execute_script('''
var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
window.current_idx -=1;
thumbnailList[window.current_idx].style.removeProperty('border'); // remove border from current thumbnail
thumbnailList[window.current_idx - 1].style.setProperty('border', '8px inset red'); // draw border on previous thumbnail
window.current_idx -=1; ''')
                          self.last_thumbnail_was = 'prevthumb'
                      else:
                          self.bro.execute_script('''
var thumbnailList = document.querySelectorAll('#thumbnail'); // get list of all thumbnail ids, gets video thumbnails
thumbnailList[window.current_idx].style.removeProperty('border'); // remove border from current thumbnail
thumbnailList[window.current_idx - 1].style.setProperty('border', '8px inset red'); // draw border on previous thumbnail
window.current_idx -=1; ''')
                          self.last_thumbnail_was = 'prevthumb'
                  except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                      print(e)
               elif "scrolldown" in self.data:
                   print('scrolldown received')
                   try:
                       self.bro.execute_script(self.js_scroll_down(350))
                   except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                       print(e)
               elif "scrollup" in self.data:
                   print('scrollup received')
                   try:
                       self.bro.execute_script(self.js_scroll_up(350))
                   except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                       print(e)
               elif "getthumbnails" in self.data:
                   print("getthumbnails received")
                   try:
                       try:
                           for _ in range(3):
                               # scroll the page so that JS loads some videos to send
                               self.bro.execute_script(self.js_scroll_down(3000))
                               time.sleep(1)
                       except (exceptions.JavascriptException, exceptions.WebDriverException) as e:
                           print(type(e), e)

                       # stuff we're going to send to client
                       elem_img = self.bro.find_elements_by_xpath('//ytd-thumbnail[@class="style-scope ytd-rich-grid-media"]/a[@id="thumbnail"]/yt-img-shadow[1]/img[@id="img"]')
                       elem_txt_href = self.bro.find_elements_by_xpath('//div[@id="dismissable"][@class="style-scope ytd-rich-grid-media"]/div[@id="details"]/div[@id="meta"]/h3[1]/a[@id="video-title-link"]')

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

                       # print("EL ###", elem_img)
                       # print("EHREF ###", elem_href)
                       # print("EVIDDESC ###", elem_vid_desc)
                       self.zip_lists(elem_img, elem_href, plst_vid_desc=elem_vid_desc)
                   except Exception as e:
                       print("getplaylistthumbnails exception: ", type(e), e)
                       self.conn.sendall(b"!! getplaylistthumbnails errored out!")
               elif "getplaylists" in self.data:
                   print("getplaylists received")
                   try:
                       try:
                           # expand "Show more" first
                           self.bro.find_element_by_xpath('//a[@title="Show more"]').click()
                       except exceptions.ElementNotInteractableException as e:
                           print("Show more exception: ", type(e), e)
                       except exceptions.NoSuchElementException as e:
                           print("Show more exception: ", type(e), e)
                           # Open hamburger menu and locate the element
                           self.bro.find_element_by_xpath("//button[@id='button'][@aria-label='Guide']").click() # hamburger element
                           time.sleep(1) # wait a bit
                           self.bro.find_element_by_xpath('//a[@title="Show more"]').click()

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
                       print(self.data.split()[1])
                       self.bro.get(self.data.split()[1])
                   except Exception as e:
                       print("playvideo EXCEPTION: ", e)

               elif "subscriptions" in self.data:
                   print("subscriptions received")
                   try:
                      self.bro.find_element_by_xpath("//a[@id='endpoint'][@title='Subscriptions']/paper-item/yt-icon").click()
                   except Exception as e:
                       print("subscriptions EXCEPTION: ", e)
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
