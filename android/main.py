#!/usr/bin/env python3

# BUG: handle utf-8 chars in thumbnail screen (e.g. japanese chars not show correctly)
__version__ = '0.9'

import threading
import os
import time

import certifi
import kivy
kivy.require('1.11.1')
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView 
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

# local imports
from client import DalyinskiClient

# Load configuration file
store = JsonStore('settings.json')
if store.exists('connection'):
    have_ip = store.get('connection')['ip']
else:
    have_ip = None

# Fix for when android is not loading the https urls (should be fixed in next kivy release)
# https://github.com/kivy/python-for-android/issues/1827
os.environ['SSL_CERT_FILE'] = certifi.where()

# variables for correct display of either play or pause button
isPaused = True
last_cmd = ''

Builder.load_string("""
<DalyinskiScrMgr>:
    id: id_scrmgr
    StartScreen:
        id: id_start_scr
    YoutubeThumbScreen:
    PlaybackScreen:
        id: id_play_scr
        name: 'playback_screen'
    ConnectServerScreen:
        id: id_conn_srv_scr
        name: 'connect_srv_screen'
    ReconnectServerScreen:
        id: id_reconn_srv_scr
        name: 'reconnect_srv_screen'
    PlaylistsScreen:

<StartScreen>:
    name: 'start_screen'
    start_scr_spinner: start_scr_spinner
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            ######################
            # Top row main menu ##
            ######################
            orientation: 'horizontal'
            size_hint: (1, 0.08)
            Spinner:
                id: start_scr_spinner
                text: 'Menu'
                size_hint: (0.2, 1.0)
                values: ("Rediscover server", "Open browser", "About")
                on_text:
                    if start_scr_spinner.text == "Rediscover server": root.manager.current = 'reconnect_srv_screen'; root.manager.transition.direction = 'right'
                    elif start_scr_spinner.text  == "About": root.show_about()
                    elif start_scr_spinner.text  == "Open browser": root.on_press_open_browser()
                    else: pass
            Label:
                size_hint: (0.8, 1.0)
                text: "dalYinski YT remote"
                canvas.before:
                    Color:
                        rgba: 0.90, 0.18, 0.15, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                
        BoxLayout:
            ######################
            # Main content area ##
            ######################
            orientation: 'vertical'
            size_hint: (1, 0.92)
            Button:
                text: 'Youtube Home'
                background_color: (1, 0, 0, 1)
                on_press: 
                    root.manager.current = 'youtube_thumb_screen' 
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Playback'
                on_press: 
                    root.manager.current = 'playback_screen' 
                    root.manager.transition.direction = 'left'

<YoutubeThumbScreen>:
    id: id_yt_th_scr
    name: 'youtube_thumb_screen'
    on_pre_enter: root.add_scroll_view()
    on_pre_leave: root.clear_scroll_view()
    on_enter: root.server_is_running()


<ConnectServerScreen>:
    press_func: root.on_press_find_server
    BoxLayout:
        orientation: 'vertical'
        Banner:
            size_hint: (1, 0.08)
            text: "Establish server connection"
        Button:
            text: "Connect to server"
            text_size: (400, None)
            size_hint: (1, 0.92)
            halign: 'center'
            on_release: 
                root.change_start_scr_spinner_txt()
                root.press_func()
                root.manager.current = 'start_screen' 
                root.manager.transition.direction = 'left'

<ReconnectServerScreen@ConnectServerScreen>:

<PlaybackScreen>:
    on_enter: root.server_is_running()
    
    btn_play_pause: btn_play_pause

    BoxLayout:
        id: id_bl_in_playback_scr
        orientation: 'vertical'
        Header:
            text: "Play controls"
        BoxLayout:
            ######################
            # Main content area ##
            ######################
            canvas.before:
                Rectangle:
                    size: self.size
                    pos: self.pos
                    source: './img/background.png'

            orientation: 'vertical'
            size_hint: (1, 0.92)
            BoxLayout:
                id: second_row_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_watch_later
                    source: './img/baseline_watch_later_black_48.png' if self.state == 'normal' else './img/outline_watch_later_black_48.png'
                    on_release: root.on_press_watch_later()
                ImageButton:
                    id: btn_scroll_up
                    source: './img/baseline_arrow_upward_black_48.png'
                    on_press: root.on_press_scroll_up()
                ImageButton:
                    id: btn_subscriptions
                    source: './img/baseline_subscriptions_black_48.png' if self.state == 'normal' else './img/outline_subscriptions_black_48.png'
                    on_release: root.on_press_subscriptions()
            BoxLayout:
                id: thumb_btns_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_prev_thumb
                    source: './img/baseline_arrow_back_black_48.png'
                    on_press: root.on_press_prev_thumb()
                ImageButton:
                    id: btn_select_thumb
                    source: './img/baseline_subdirectory_arrow_left_black_48.png'
                    on_press: root.on_press_select_thumb()
                ImageButton:
                    id: btn_next_thumb
                    source: './img/baseline_arrow_forward_black_48.png'
                    on_press: root.on_press_next_thumb()
            BoxLayout:
                id: cpt_sd_st_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_captions
                    source: './img/baseline_closed_caption_black_48.png' if self.state == 'normal' else './img/outline_closed_caption_black_48.png'
                    on_release: root.on_press_captions()
                ImageButton:
                    id: btn_scroll_down
                    source: './img/baseline_arrow_downward_black_48.png'
                    on_press: root.on_press_scroll_down()
                ImageButton:
                    id: btn_switch_tab
                    source: './img/baseline_tab_black_48.png' if self.state == 'normal' else './img/baseline_tab_unselected_black_48.png'
                    on_release: root.on_press_switch_tab()
            BoxLayout:
                id: playback_btns_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_play_previous
                    source: './img/baseline_skip_previous_black_48.png' if self.state == 'normal' else './img/outline_skip_previous_black_48.png'
                    on_release: root.on_press_play_previous()
                PlayPauseButton:
                    id: btn_play_pause
                    on_press: root.on_press_play_pause()
                ImageButton:
                    id: btn_play_next
                    source: './img/baseline_skip_next_black_48.png' if self.state == 'normal' else './img/outline_skip_next_black_48.png'
                    on_release: root.on_press_play_next()
            BoxLayout:
                id: ff_rew_home_btns_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_rewind
                    source: './img/baseline_replay_5_black_48.png'
                    on_press: root.on_press_rewind()
                ImageButton:
                    id: btn_home
                    # source: './img/baseline_fullscreen_black_48.png' if self.state == 'normal' else './img/outline_home_black_48.png'
                    source: './img/baseline_home_black_48dp.png' if self.state == 'normal' else './img/outline_home_black_48.png'
                    on_release: root.on_press_go_home()
                ImageButton:
                    id: btn_forward
                    source: './img/baseline_forward_5_black_48.png'
                    on_press: root.on_press_fforward()

            Button:
                id: btn_fullscreen
                text: 'Fullscreen'
                pos_hint: {'center_x': .5, 'center_y': .5}
                on_press: root.on_press_fullscreen()
            

<PlaylistsScreen>:
    id: id_playlists_scr
    name: 'playlists_screen'
    on_enter: root.add_scroll_view()
    on_leave: 
        root.clear_scroll_view()
        app.last_screen = "playlists_screen"

<Banner>: # Label class
    size_hint: (0.6, 1.0)
    bold: True
    canvas.before:
        Color:
            rgba: 0.90, 0.18, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size

<Header>: # This is a BoxLayout
    ######################
    # Top row main menu ##
    ######################
    id: id_header
    text: ''
    orientation: 'horizontal'
    size_hint: (1, 0.08)
    pos_hint: {'top': 1}
    Button:
        size_hint: (0.2, 1.0)
        on_release: 
            root.on_press_go_home()
            app.last_screen = "start_screen"
            app.root.current = 'start_screen'
            app.root.transition.direction = 'right'
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/baseline_arrow_back_black_48dp.png' 
            Label:
                size_hint: (0.6, 1.0)
                text: "Go Back"
                halign: 'left'
                valign: 'middle'
                font_size: '11sp'
                text_size: self.size
                bold: 'true'
    Banner:
        text: root.text
    Button:
        text: "Playlists"
        size_hint: (0.2, 1.0)
        on_release:
            app.root.current = 'playlists_screen'
            app.root.transition.direction = 'left'
    #Spinner:
    #    id: id_playlist_spinner
    #    text: "Playlists"
    #    size_hint: (0.2, 1.0)
    #    values: ("Trending", "Subscriptions", "Library", "History")
    #    on_text: 
    #        if id_playlist_spinner.text == "Subscriptions": root.go_subscriptions(); id_playlist_spinner.text = "Playlists"
    #        else: pass
    

<ThumbScreenHeader@Header>:
    text: 'YouTube Home'

<PlaylistsHeader@Header>:
    text: 'Your playlists'

<ScrollableViewPlaylists>:
    scroll_view_plst: scroll_view_plst

    size_hint: 1, 0.92 # adapt to the header that goes above scrollable GridLayout

    GridLayout:
        id: scroll_view_plst
        row_default_height: 100
        cols: 1
        spacing: 1
        size_hint_y: None
        padding: (10, 0)

<ScrollableViewYThumbScreen>:
    scroll_view_yt_gl: scroll_view_yt_gl

    size_hint: 1, 0.92 # adapt to the header that goes above scrollable GridLayout

    on_scroll_stop: root.update_content()

    # videos are dynamically added into this grid layout
    GridLayout:
        id: scroll_view_yt_gl
        row_default_height: 300
        cols: 3
        spacing: 1
        size_hint_y: None

# These 3 widgets are dynamically added to GridLayout under ScrollableViewYThumbScreen above
<YTimg>:

<YTlbl>:
    text_size: self.size
    valign: 'center'
    padding_x: '6sp'
    height: self.texture_size[1]
    max_lines: 3

<YTPlay>:
    text: "Play"
    on_release: 
        root.play_video()
        app.root.current = 'playback_screen'
        app.root.transition.direction = 'right'

# Dynamically added to ScrollableViewPlaylists
<PlstBtn>:
    on_press: 
        root.select_playlist()
        app.root.current = 'youtube_thumb_screen'


""")

def show_popup(message='Info', dismiss=False):
    popup = Popup(title='Info',
    content=Label(text=message),
    size_hint=(0.8, 0.8), size=(600, 400),
    auto_dismiss=dismiss)
    return popup

class Banner(Label):
    pass


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def go_subscriptions(self):
        c = DalyinskiClient()
        c.command(b'subscriptions')

    def on_press_go_home(self):
        PlaybackScreen().on_press_go_home()

class ThumbScreenHeader(Header):
    pass


class PlaylistsHeader(Header):
    pass


class YTimg(AsyncImage):
    def __init__(self, imgsrc, **kwargs):
        super().__init__(**kwargs)
        self.source = imgsrc
        

class YTlbl(Label):
    def __init__(self, labeltext, **kwargs):
        super().__init__(**kwargs)
        self.text = labeltext


video_thumb_urls = [] # this is a list of tuples
class ScrollableViewYThumbScreen(ScrollView):
    scroll_view_yt_gl = ObjectProperty()

    def __init__(self, client_cmd=b'getthumbnails', **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.width, Window.height)
        self.scroll_view_yt_gl.bind(minimum_height=self.scroll_view_yt_gl.setter('height'))
        self.chunk_index = 0 # keep track on which chunk in the list we are
        self.video_thumb_chunk = []
        # If we are coming from playlists screen, send a different command to fetch correct results from server and wait until the youtube playlist page is loaded on server side
        if app.last_screen == "playlists_screen":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            self.pf.open()
            time.sleep(1)
            self.client_cmd = b'getplaylistthumbnails'
        elif app.last_screen == "start_screen":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            self.pf.open()
            c = DalyinskiClient()
            self.client_cmd = client_cmd
        self.get_thumbnails()

    def get_thumbnails(self, chunk_idx=0):
        ''' We can't do any UI updates from a separate thread.
        That's why we are calling a separate function (video_urls()) from
        the threaded function (_get_thumbnails()) and scheduling
        it on the main thread via @mainthread decorator from kivy.clock 
        module '''
        t = threading.Thread(target=self._get_thumbnails, args=(chunk_idx,), daemon=True)
        t.start()

    def _get_thumbnails(self, chunk_idx=0):
        c = DalyinskiClient()
        # TODO: maybe use a decorator for checking if the server is up, so that it can be reused
        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the server is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
        else:
            global video_thumb_urls
            video_thumb_urls = c.recv_thumb_list(self.client_cmd)
            self.video_thumb_chunk = list(self.divide_chunks(video_thumb_urls, 10)) # a list of lists of videos
            self.video_urls(self.video_thumb_chunk, chunk_idx=0)
            self.pf.dismiss()
            Logger.debug(f"dalYinskiApp: video thumb chunks >> {self.video_thumb_chunk}")

    @mainthread
    def video_urls(self, video_thumb_chunk, chunk_idx=0):
        try:
            vid_sublist = video_thumb_chunk[chunk_idx]
            Logger.info(f"dalYinskiApp: Chunk index: {self.chunk_index}, of list length {len(video_thumb_chunk)}")
            for thumb in vid_sublist:
                # Logger.info(f"dalYinskiApp: DESCRIPTION: {thumb[0]}")
                # Logger.info(f"dalYinskiApp: IMAGE LINK: {thumb[1]}")
                # Logger.info(f"dalYinskiApp: VIDEO LINK: {thumb[2]}")
                self.scroll_view_yt_gl.add_widget(YTimg(thumb[1]))
                self.scroll_view_yt_gl.add_widget(YTlbl(thumb[0]))
                self.scroll_view_yt_gl.add_widget(YTPlay(thumb[2])) # send video url to constructor
            self.chunk_index += 1
        except IndexError as e:
            Logger.info(f"dalYinskiApp: {type(e)} {e}")

    def update_content(self):
        if round(self.scroll_y, 2) < 0:
            Logger.debug("dalYinskiApp: *** UPDATE CONTENT ***")
            Logger.debug(f"dalYinskiApp: Chunk idx after {self.chunk_index}")
            self.video_urls(self.video_thumb_chunk, self.chunk_index)

    def divide_chunks(self, l, n): 
        '''
        Yield successive n-sized 
        chunks from list l. '''
          
        # looping till length l 
        for i in range(0, len(l), n):  
            yield l[i:i + n] 
    
class ScrollableViewPlaylists(ScrollView):
    scroll_view_plst = ObjectProperty()
            
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.width, Window.height)
        self.scroll_view_plst.bind(minimum_height=self.scroll_view_plst.setter('height'))
        self.get_playlists()

    def get_playlists(self):
        t = threading.Thread(target=self._get_playlists, daemon=True)
        t.start()

    def _get_playlists(self):
        c = DalyinskiClient()

        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the server is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
        else:
            p = show_popup("Fetching playlists... \nPlease wait.")
            p.open()
            usr_playlists = c.recv_playlists(b'getplaylists') # a list of tuples of playlist name and link
            Logger.debug(f"dalYinskiApp: Got list of playlists: {usr_playlists}")
            for plst in usr_playlists:
                self.scroll_view_plst.add_widget(PlstBtn(str(plst[1]), text=str(plst[0]))) # plst[1] is playlist link (sent to the constructor in order to open it), plst[0] is playlist name
            p.dismiss()


#########################
# Custom button classes #
#########################
class YTPlay(Button):
    def __init__(self, vidurl, **kwargs):
        super().__init__(**kwargs)
        self.vidurl = vidurl

    # def on_parent(self, obj, parent):
        ''' Once this button widget gets a parent set its height
        relative to parents. We can't do this in kv language
        because this button is dynamically added.
        '''
        # self.height = self.parent.height * 2
        # self.height = 100

    def play_video(self):
        t = threading.Thread(target=self._play_video, daemon=True)
        t.start()

    def _play_video(self):
        ''' Send playvideo command + video url from the video_thumb_urls list
        which gets passed in the constructor above as vidurl variable
        so that the server can start video. '''
        c = DalyinskiClient()
        c.command(b'playvideo' + b' ' + bytes(self.vidurl, 'utf-8'))


class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PlayPauseButton(ButtonBehavior, Image):
    ''' Custom button class '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source='./img/baseline_play_circle_filled_black_48.png'

    def on_press(self):
        ''' Once the on_press signal is received check if the variable isPaused is set to True.
        If it is true display the play icon so that the user can know that the button resumes play.
        If false, so it's paused, on_press will play the video and display the pause icon.
        Update what was the last command. '''
        # TODO: Maybe just send the info on whether the video is playing from the server?
        global isPaused
        global last_cmd
        if not isPaused:
            self.source = './img/baseline_play_circle_filled_black_48.png'
            isPaused = True
        else: 
            self.source = './img/baseline_pause_circle_filled_black_48.png'
            isPaused = False
        last_cmd = 'playpause'

class PlstBtn(Button):
    def __init__(self, vidurl, **kwargs):
        super().__init__(**kwargs)
        self.vidurl = vidurl

    def select_playlist(self):
        t = threading.Thread(target=self._select_playlist, daemon=True)
        t.start()

    def _select_playlist(self):
        ''' Send playvideo command + video url from the list
        which gets passed in the constructor above as vidurl variable
        so that the server can start video. '''
        c = DalyinskiClient()
        c.command(b'playvideo' + b' ' + bytes(self.vidurl, 'utf-8'))


#########################
#       Screens         #
#########################
class StartScreen(Screen):
    start_scr_spinner = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info(f"dalYinskiApp: Last screen was: {app.last_screen}")
        app.last_screen = "start_screen"

    def show_about(self):
        popup = Popup(title="About",
                content=Label(text=f"Ugly app for Youtube remote control :-)\n\
                        Version: {__version__}"),
        size_hint=(0.8, 0.8), size=(600, 400),
        auto_dismiss=True)
        popup.open()
        # Logger.info(f"dalYinskiApp: {self.parent.ids}")
        self.parent.ids.id_start_scr.start_scr_spinner.text = 'Menu'

    def _on_press_open_browser(self):
        ''' Private function to call with threading, to prevent gui blocking '''
        p = show_popup("Opening web browser...\nPlease wait.")
        p.open()
        c = DalyinskiClient()
        c.command(b'fbro')
        p.dismiss()

    def on_press_open_browser(self):
        ''' Threading function to call the "real" function '''
        t = threading.Thread(target=self._on_press_open_browser, args=())
        t.start()

class ConnectServerScreen(Screen):

    def _on_press_find_server(self):
        ''' If the server changed its IP, reset the IP
        in config file, so the client.py can run the redisovery
        routine. '''
        Logger.info("dalYinskiApp: Resetting IP...")
        p = show_popup("Finding server IP...\nPlease wait.")
        p.open()
        store.put('connection', ip='')
        c = DalyinskiClient()
        c.command(b'ping')
        p.dismiss()
        
    def on_press_find_server(self):
        t = threading.Thread(target=self._on_press_find_server, args=())
        t.start()

    def change_start_scr_spinner_txt(self):
        self.parent.ids.id_start_scr.start_scr_spinner.text = 'Menu'

class ReconnectServerScreen(Screen):
    pass


class YoutubeThumbScreen(Screen):
    def add_scroll_view(self):
        t = threading.Thread(target=self._add_scroll_view, args=())
        t.start()

    def _add_scroll_view(self):
        self.add_widget(ScrollableViewYThumbScreen())
        self.add_widget(ThumbScreenHeader())
        Logger.info(f"dalYinskiApp: Current screen: youtube_thumb_screen; Last screen was: {app.last_screen}")
        app.last_screen = "youtube_thumb_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

    def server_is_running(self):
        c = DalyinskiClient()
        # if the server isn't running switch back to start screen
        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the server is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
            self.manager.current = 'start_screen'
        else:
            pass

class PlaylistsScreen(Screen):
    def add_scroll_view(self):
        self.add_widget(ScrollableViewPlaylists())
        self.add_widget(PlaylistsHeader())
        Logger.info(f"dalYinskiApp: Current screen: PlaylistsScreen; Last screen was: {app.last_screen}")
        app.last_screen = "playlists_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

class PlaybackScreen(Screen):
    btn_play_pause = ObjectProperty()

    def server_is_running(self):
        c = DalyinskiClient()
        # if the server isn't running switch back to start screen
        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the server is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
            self.manager.current = 'start_screen'
        else:
            pass

    # TODO: maybe use a singleton instead of instantiating new class in every call
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons

    def on_press_play_previous(self):
        # TODO: this is buggy, rework it
        ''' For this method and the one below which plays next, we want to update the icon
        only when the video is paused and we are skipping to the next video. Youtube plays
        the next or previous video automatically when skipping so we are setting the pause
        icon. Video will be playing so the paused state is False. '''
        global isPaused
        c = DalyinskiClient()
        c.command(b'playprevious')
        if not isPaused and last_cmd == 'prevornext':
            pass
        elif not isPaused and last_cmd == 'playpause':
            pass
        elif isPaused:
            self.btn_play_pause.source = './img/baseline_pause_circle_filled_black_48.png'
            isPaused = False
        # print('PreviousNext ==>',isPaused)

    def on_press_play_pause(self):
        c = DalyinskiClient()
        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the browser is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
        else:
            c.command(b'playpause')
       
    def on_press_play_next(self):
        global isPaused
        c = DalyinskiClient()
        c.command(b'playnext')
        if not isPaused and last_cmd == 'prevornext':
            pass
        elif not isPaused and last_cmd == 'playpause':
            pass
        elif isPaused:
            self.btn_play_pause.source = './img/baseline_pause_circle_filled_black_48.png'
            isPaused = False
        # print('PreviousNext ==>',isPaused)

    def on_press_watch_later(self):
        c = DalyinskiClient()
        c.command(b'watchlater')

    def on_press_go_home(self):
        c = DalyinskiClient()
        c.command(b'gohome')

    def on_press_fullscreen(self):
        c = DalyinskiClient()
        c.command(b'fullscreen')

    def on_press_captions(self):
        c = DalyinskiClient()
        c.command(b'captions')

    def on_press_switch_tab(self):
        c = DalyinskiClient()
        c.command(b'switchtab')

    def on_press_fforward(self):
        c = DalyinskiClient()
        c.command(b'fforward')

    def on_press_rewind(self):
        c = DalyinskiClient()
        c.command(b'rewind')

    def on_press_next_thumb(self):
        c = DalyinskiClient()
        c.command(b'nextthumb')

    def on_press_prev_thumb(self):
        c = DalyinskiClient()
        c.command(b'prevthumb')

    def on_press_select_thumb(self):
        c = DalyinskiClient()
        c.command(b'selectthumb')

    def on_press_scroll_down(self):
        c = DalyinskiClient()
        c.command(b'scrolldown')

    def on_press_scroll_up(self):
        c = DalyinskiClient()
        c.command(b'scrollup')

    def on_press_subscriptions(self):
        c = DalyinskiClient()
        c.command(b'subscriptions')

class DalyinskiScrMgr(ScreenManager):
    pass


class MainApp(App):
    title = "DalYinski"
    last_screen = None

    def build(self):
        screen_mgr = DalyinskiScrMgr()
        # if we don't have a server ip stored in the config show connection screen
        if have_ip:
            screen_mgr.current = 'start_screen'
        else:
            screen_mgr.current = 'connect_srv_screen'
        return screen_mgr
      
if __name__ == '__main__':
    app = MainApp()
    app.run()
