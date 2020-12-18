#!/usr/bin/env python3

__version__ = '0.13'

import threading
import os
import time

import kivy
kivy.require('2.0.0')
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
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView 
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore
from kivy.uix.recycleview import RecycleView

# local imports
from client import DalyinskiClient

# Load configuration file
store = JsonStore('settings.json')
if store.exists('connection'):
    have_ip = store.get('connection')['ip']
else:
    have_ip = None

Builder.load_string("""
<DalyinskiScrMgr>:
    id: id_scrmgr
    StartScreen:
        id: id_start_scr
        name: 'start_screen'
    YoutubeThumbScreen:
        id: id_yt_th_scr
        name: 'youtube_thumb_screen'
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
        id: id_playlists_scr
        name: 'playlists_screen'
    WatchLaterScreen:
        id: id_watchlater_scr
        name: 'watchlater_screen'
    SubscriptionsScreen:
        id: id_subs_scr
        name: 'subs_screen'


<DropDown>:
    # Specify custom button width in Spinner below
    auto_width: False
    width: 400

<StartScreen>:
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
            Button:
                text: "Playback"
                size_hint: (0.2, 1.0)
                on_release:
                    app.last_btn_pressed = "playback"
                    app.root.current = 'playback_screen'
                    app.root.transition.direction = 'left'
                
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
                    app.last_btn_pressed = "ythome"
                    root.manager.current = 'youtube_thumb_screen' 
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Playlists'
                background_color: (0, 1, 0, 1)
                on_press: 
                    app.last_btn_pressed = "playlists"
                    root.manager.current = 'playlists_screen' 
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Subscriptions'
                background_color: (0, 0, 1, 1)
                on_press: 
                    app.last_btn_pressed = "subscriptions"
                    root.manager.current = 'subs_screen' 
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Watch Later'
                background_color: (0.5, 0.5, 0, 1)
                on_press: 
                    app.last_btn_pressed = "watchlater"
                    root.manager.current = 'watchlater_screen' 
                    root.manager.transition.direction = 'left'

<YoutubeThumbScreen>:
    on_pre_enter: app.server_is_running()
    on_enter: root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<SubscriptionsScreen>:
    on_pre_enter: app.server_is_running()
    on_enter: root.add_scroll_view()
    on_leave: root.clear_scroll_view()

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

<WatchLaterScreen>:
    on_pre_enter: app.server_is_running()
    on_enter: root.add_scroll_view()
    on_leave: 
        root.clear_scroll_view()


<PlaylistsScreen>:
    on_pre_enter: app.server_is_running()
    on_enter: root.add_scroll_view()
    on_leave: 
        root.clear_scroll_view()
        app.last_screen = "playlists_screen"

<ReconnectServerScreen@ConnectServerScreen>:

<PlaybackScreen>:
    on_pre_enter: app.server_is_running()
    
    btn_play_pause: btn_play_pause

    BoxLayout:
        id: id_bl_in_playback_scr
        orientation: 'vertical'
        Header:
            text: "Playback"
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
                id: id_cc_vol_up_dwn
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_volup
                    source: './img/baseline_volume_up_black_48dp.png' if self.state == 'normal' else './img/outline_volume_up_black_48.png'
                    on_press: root.on_press_vol_up()
                ImageButton:
                    id: btn_captions
                    source: './img/baseline_closed_caption_black_48dp.png' if self.state == 'normal' else './img/outline_closed_caption_black_48.png'
                    on_release: root.on_press_captions()
                ImageButton:
                    id: btn_voldwn
                    source: './img/baseline_volume_down_black_48dp.png' if self.state == 'normal' else './img/outline_volume_down_black_48.png'
                    on_release: root.on_press_vol_down()
            BoxLayout:
                id: playback_btns_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_play_previous
                    source: './img/baseline_skip_previous_black_48dp.png' if self.state == 'normal' else './img/outline_skip_previous_black_48.png'
                    on_release: root.on_press_play_previous()
                PlayPauseButton:
                    id: btn_play_pause
                    source: './img/baseline_play_circle_filled_black_36dp.png' if self.state == 'normal' else './img/outline_play_circle_outline_black_48.png'
                    on_press: root.on_press_play_pause()
                ImageButton:
                    id: btn_play_next
                    source: './img/baseline_skip_next_black_48dp.png' if self.state == 'normal' else './img/outline_skip_next_black_48.png'
                    on_release: root.on_press_play_next()
            BoxLayout:
                id: ff_rew_home_btns_lyt
                orientation: 'horizontal'
                spacing: 1
                ImageButton:
                    id: btn_rewind
                    source: './img/baseline_replay_5_black_48dp.png' if self.state == 'normal' else './img/outline_replay_5_black_48.png'
                    on_press: root.on_press_rewind()
                ImageButton:
                    id: btn_home
                    source: './img/baseline_home_black_36dp.png' if self.state == 'normal' else './img/outline_home_black_48.png'
                    on_release: root.on_press_go_home()
                ImageButton:
                    id: btn_forward
                    source: './img/baseline_forward_5_black_48dp.png' if self.state == 'normal' else './img/outline_forward_5_black_48.png'
                    on_press: root.on_press_fforward()

            Button:
                id: btn_fullscreen
                text: 'Fullscreen'
                pos_hint: {'center_x': .5, 'center_y': .5}
                on_press: root.on_press_fullscreen()

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
            if app.in_fullscreen: app.root.ids.id_play_scr.on_press_fullscreen()
            else: pass
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
        text: "Playback"
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "playback"
            app.root.current = 'playback_screen'
            app.root.transition.direction = 'left'
    

<ThumbScreenHeader@Header>:
    text: "Videos"

<PlaylistsHeader@Header>:
    text: "Playlists"

<SubscriptionsHeader@Header>:
    text: "Subscriptions"

<WatchLaterHeader@Header>:
    text: "Watch Later"

<ScrollableViewWatchLater>:
    scroll_view_wl: scroll_view_wl

    size_hint: 1, 0.92 # adapt to the header that goes above scrollable GridLayout

    GridLayout:
        # id: scroll_view_plst
        row_default_height: 100
        cols: 1
        spacing: 1
        size_hint_y: None
        padding: (10, 0)

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
    id: id_scroll_view_yt_t_scr

    size_hint: 1, 0.92 # adapt to the header that goes above scrollable GridLayout

    RecycleView:
        id: id_rv
        data: root.video_list # a list of dictionaries which get passed to VideoItem
        viewclass: 'VideoItem'
        RecycleBoxLayout:
            default_size: None, None
            default_size_hint: 1, None
            size_hint: (1, None)
            height: self.minimum_height
            orientation: 'vertical'
            padding: [0, 10]

<VideoItem>: # GridLayout
    id: id_video_item
    # values below are placeholders which get replaced by the data from RecycleView above
    image_link: "link"
    image_desc: "text"
    video_link: "link"
    
    cols: 1
    height: self.minimum_height
    BoxLayout:
        size_hint: (1, None)
        height: self.minimum_height
        orientation: 'vertical'
        AsyncImage:
            source: root.image_link
            height: sp(200)
            size_hint: (1, None)
            allow_stretch: True
        Label:
            text: root.image_desc
            text_size: self.size
            font_size: '10sp'
            valign: 'center'
            halign: 'center'
            height: sp(50)
            size_hint: (1, None)
            max_lines: 3
        YTPlay:
            height: sp(50)
            size_hint: (1, None)
            on_release: 
                self.play_video(root.video_link)

<YTPlay>:
    text: "Play"
    on_release: 
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


class ThumbScreenHeader(Header):
    pass


class PlaylistsHeader(Header):
    pass


class SubscriptionsHeader(Header):
    pass


class WatchLaterHeader(Header):
    pass


class VideoItem(GridLayout):
    pass


#########################
#  Scrollable views     #
#########################
class ScrollableViewYThumbScreen(ScrollView):
    video_list = ListProperty()

    def __init__(self, client_cmd=b'getthumbnails', **kwargs):
        super().__init__(**kwargs)
        # Send different command to server depending on which button was pressed
        if app.last_btn_pressed == "ythome":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            PlaybackScreen().on_press_go_home()
            self.pf.open()
            time.sleep(1) # wait a bit for the page to load
            self.client_cmd = client_cmd
        elif app.last_btn_pressed == "watchlater":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            PlaybackScreen().on_press_watch_later()
            self.pf.open()
            time.sleep(1)
            self.client_cmd = b'getplaylistthumbnails'
        elif app.last_screen == "playlists_screen" or app.last_btn_pressed == "playlists":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            self.pf.open()
            time.sleep(1)
            self.client_cmd = b'getplaylistthumbnails'
        elif app.last_screen == "start_screen" and app.last_btn_pressed == "subscriptions":
            self.pf = show_popup("Fetching videos... \nPlease wait.")
            PlaybackScreen().on_press_subscriptions()
            self.pf.open()
            time.sleep(1)
            self.client_cmd = b'getsubscriptionhumbnails'
        self.get_thumbnails()

    def get_thumbnails(self):
        self.t = threading.Thread(target=self._get_thumbnails, args=(), daemon=True)
        self.t.start()

    def _get_thumbnails(self):
        c = DalyinskiClient()
        # TODO: maybe use a decorator for checking if the server is up, so that it can be reused
        video_thumb_urls = c.recv_thumb_list(self.client_cmd)
        self.video_urls(video_thumb_urls)
        self.pf.dismiss()

    def video_urls(self, video_thumb_urls):
        try:
            for thumb in video_thumb_urls:
                loop_video_data_dict = dict()
                Logger.debug(f"dalYinskiApp: DESCRIPTION: {thumb[0]}")
                Logger.debug(f"dalYinskiApp: IMAGE LINK: {thumb[1]}")
                Logger.debug(f"dalYinskiApp: VIDEO LINK: {thumb[2]}")
                loop_video_data_dict["image_link"] = thumb[1]
                loop_video_data_dict["image_desc"] = thumb[0]
                loop_video_data_dict["video_link"] = thumb[2]
                self.video_list.append(loop_video_data_dict)
        except IndexError as e:
            Logger.info(f"dalYinskiApp: {type(e)} {e}")

    
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

        p = show_popup("Fetching playlists... \nPlease wait.")
        p.open()
        usr_playlists = c.recv_playlists(b'getplaylists') # a list of tuples of playlist name and link
        Logger.debug(f"dalYinskiApp: Got list of playlists: {usr_playlists}")
        for plst in usr_playlists:
            self.scroll_view_plst.add_widget(PlstBtn(str(plst[1]), text=str(plst[0]))) # plst[1] is playlist link (sent to the constructor in order to open it), plst[0] is playlist name
        p.dismiss()


class ScrollableViewWatchLater(ScrollView):
    pass

#########################
# Custom button classes #
#########################
class YTPlay(Button):
    def __init__(self, vidurl=None, **kwargs):
        super().__init__(**kwargs)
        self.vidurl = vidurl

    def play_video(self, vidurl):
        t = threading.Thread(target=self._play_video, args=(vidurl, ), daemon=True)
        t.start()

    def _play_video(self, vidurl):
        ''' Send playvideo command + video url from the video_thumb_urls list
        which gets passed in the constructor above as vidurl variable
        so that the server can start video. '''
        c = DalyinskiClient()
        c.command(b'playvideo' + b' ' + bytes(vidurl, 'utf-8'))


class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PlayPauseButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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
        Logger.debug(f"dalYinskiApp: {self.parent.ids}")
        self.parent.ids.id_start_scr.start_scr_spinner.text = 'Menu'

    def on_press_open_browser(self):
        ''' Threading function to call the "real" function '''
        t = threading.Thread(target=self._on_press_open_browser, args=())
        t.start()

    def _on_press_open_browser(self):
        ''' Private function to call with threading, to prevent gui blocking '''
        p = show_popup("Opening web browser...\nPlease wait.")
        p.open()
        c = DalyinskiClient()
        c.command(b'fbro')
        p.dismiss()


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
        self.add_widget(ScrollableViewYThumbScreen())
        self.add_widget(ThumbScreenHeader())
        Logger.info(f"dalYinskiApp: Current screen: youtube_thumb_screen; Last screen was: {app.last_screen}")
        app.last_screen = "youtube_thumb_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

class PlaylistsScreen(Screen):
    def add_scroll_view(self):
        self.add_widget(ScrollableViewPlaylists())
        self.add_widget(PlaylistsHeader())
        Logger.info(f"dalYinskiApp: Current screen: playlists_screen; Last screen was: {app.last_screen}")
        app.last_screen = "playlists_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

class WatchLaterScreen(Screen):
    def add_scroll_view(self):
        self.add_widget(ScrollableViewYThumbScreen())
        self.add_widget(WatchLaterHeader())
        Logger.info(f"dalYinskiApp: Current screen: watchlater_screen; Last screen was: {app.last_screen}")
        app.last_screen = "watchlater_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

class SubscriptionsScreen(Screen):
    def add_scroll_view(self):
        self.add_widget(ScrollableViewYThumbScreen())
        self.add_widget(SubscriptionsHeader())
        Logger.info(f"dalYinskiApp: Current screen: subs_screen; Last screen was: {app.last_screen}")
        app.last_screen = "subs_screen"

    def clear_scroll_view(self):
        self.clear_widgets()

class PlaybackScreen(Screen):
    def on_press_play_previous(self):
        c = DalyinskiClient()
        c.command(b'playprevious')

    def on_press_play_pause(self):
        c = DalyinskiClient()
        c.command(b'playpause')
       
    def on_press_play_next(self):
        c = DalyinskiClient()
        c.command(b'playnext')

    def on_press_watch_later(self):
        c = DalyinskiClient()
        c.command(b'watchlater')

    def on_press_go_home(self):
        c = DalyinskiClient()
        c.command(b'gohome')

    def on_press_fullscreen(self):
        c = DalyinskiClient()
        c.command(b'fullscreen')
        if not app.in_fullscreen:
            app.in_fullscreen = True
        else:
            app.in_fullscreen = False

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

    def on_press_subscriptions(self):
        c = DalyinskiClient()
        c.command(b'subscriptions')

    def on_press_vol_up(self):
        c = DalyinskiClient()
        c.command(b'volup')

    def on_press_vol_down(self):
        c = DalyinskiClient()
        c.command(b'voldown')

class DalyinskiScrMgr(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.go_back)

    def go_back(self, window, key, *largs):
        if key == 27:
            self.current = 'start_screen'
            return True


class MainApp(App):
    title = "DalYinski"
    last_screen = None
    last_btn_pressed = None
    # Are we in fullscreen?
    in_fullscreen = False


    def build(self):
        self.screen_mgr = DalyinskiScrMgr()
        # if we don't have a server ip stored in the config show connection screen
        if have_ip:
            self.screen_mgr.current = 'start_screen'
        else:
            self.screen_mgr.current = 'connect_srv_screen'
        return self.screen_mgr
      
    def server_is_running(self):
        c = DalyinskiClient()
        # if the server isn't running switch back to start screen
        if not c.SERVER_RUNNING:
            p = show_popup("It looks like the server is not running.\nPlease open it.",
                            dismiss=True)
            p.open()
            self.screen_mgr.current = 'start_screen'
        else:
            pass

if __name__ == '__main__':
    app = MainApp()
    app.run()
