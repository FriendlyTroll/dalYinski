#!/usr/bin/env python3

__version__ = '1.4'

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
store = JsonStore('../settings.json')
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
    PlaylistVideosScreen:
        id: id_playlist_videos_screen
        name: 'playlist_videos_screen'
    MyChannelsScreen:
        id: id_my_channels_screen
        name: 'my_channels_screen'
    ChannelVideosScreen:
        id: id_channel_videos_screen
        name: 'channel_videos_screen'



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
                size_hint: (0.2, 1.0)
                values: ("Rediscover server", "Open browser", "About")
                on_text:
                    if start_scr_spinner.text == "Rediscover server": root.manager.current = 'reconnect_srv_screen'; root.manager.transition.direction = 'right'
                    elif start_scr_spinner.text  == "About": root.show_about()
                    elif start_scr_spinner.text  == "Open browser": root.on_press_open_browser()
                    else: pass
                BoxLayout:
                    pos: self.parent.pos
                    size: self.parent.size
                    Image:
                        source: './img/baseline_menu_black_48dp.png' 
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
                size_hint: (0.2, 1.0)
                on_release:
                    app.last_btn_pressed = "playback"
                    app.root.current = 'playback_screen'
                    app.root.transition.direction = 'left'
                BoxLayout:
                    pos: self.parent.pos
                    size: self.parent.size
                    Image:
                        source: './img/baseline_settings_remote_black_48dp.png' 
                
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
                text: 'My Channels'
                background_color: (0.2, 0.5, 1, 1)
                on_press: 
                    app.last_btn_pressed = "mychannels_btn"
                    root.manager.current = 'my_channels_screen' 
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Watch Later'
                background_color: (0.5, 0.5, 0, 1)
                on_press: 
                    app.last_btn_pressed = "watchlater"
                    root.manager.current = 'watchlater_screen' 
                    root.manager.transition.direction = 'left'

<PlaylistVideosScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<YoutubeThumbScreen>:
    on_pre_enter: 
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<SubscriptionsScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<ConnectServerScreen>:
    press_func: root.on_press_find_server
    BoxLayout:
        orientation: 'vertical'
        Banner: # Label
            size_hint: (1, 0.4)
            text_size: root.width, None
            halign: 'center'
            text: "Before using this app please make sure you have installed and started the server application on your desktop/laptop computer first. You can download the new version of the server at https://friendlytroll.github.io/dalYinski. Then hit the button below to connect."
        Button:
            text: "Connect to server"
            text_size: (400, None)
            size_hint: (1, 0.6)
            halign: 'center'
            on_release: 
                root.change_start_scr_spinner_txt()
                root.press_func()
                root.manager.current = 'start_screen' 
                root.manager.transition.direction = 'left'

<WatchLaterScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<PlaylistsScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<MyChannelsScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

<ChannelVideosScreen>:
    on_pre_enter:
        app.server_is_running()
        root.add_scroll_view()
    on_leave: root.clear_scroll_view()

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
                on_press: 
                    if app.in_fullscreen: root.on_press_fullscreen(); app.in_fullscreen = False
                    else: root.on_press_fullscreen(); app.in_fullscreen = True

<Banner>: # Label class
    size_hint: (0.6, 1.0)
    bold: True
    canvas.before:
        Color:
            rgba: 0.90, 0.18, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size

<Header>: # BoxLayout
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
    Banner:
        text: root.text
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "playback"
            app.root.current = 'playback_screen'
            app.root.transition.direction = 'left'
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                source: './img/baseline_settings_remote_black_48dp.png' 
    

<PlaylistVideosHeader@Header>:
    text: "Playlist videos"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "refresh_button"
            app.refresh_vids(where="playlist_thumbs")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<YoutubeThumbScreenHeader@Header>:
    text: "Home Videos"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "refresh_button"
            app.refresh_vids(where="ythome")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<PlaylistsHeader@Header>:
    text: "Playlists"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.refresh_vids(where="playlists")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<SubscriptionsHeader@Header>:
    text: "Subscriptions"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.refresh_vids(where="subscriptions")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<WatchLaterHeader@Header>:
    text: "Watch Later"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.refresh_vids(where="watch_later")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<ChannelVideosHeader@Header>:
    text: "Channel videos"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "refresh_button"
            app.refresh_vids(where="channel_thumbs")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

<MyChannelsHeader@Header>:
    text: "My Channels"
    Button:
        size_hint: (0.2, 1.0)
        on_release:
            app.last_btn_pressed = "refresh_button"
            app.refresh_vids(where="my_channels")
        BoxLayout:
            pos: self.parent.pos
            size: self.parent.size
            Image:
                size_hint: (0.4, 1.0)
                source: './img/round_refresh_black_48dp.png' 

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
        row_default_height: 200
        cols: 1
        spacing: 1
        size_hint_y: None
        padding: (10, 0)


<ScrollableViewMyChannels>:
    scroll_view_plst: scroll_view_plst

    size_hint: 1, 0.92 # adapt to the header that goes above scrollable GridLayout

    GridLayout:
        id: scroll_view_plst
        row_default_height: 200
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
    on_release: 
        app.root.current = 'playback_screen'
        app.root.transition.direction = 'right'
    BoxLayout:
        pos: self.parent.pos
        size: self.parent.size
        Image:
            source: './img/outline_play_circle_outline_black_48.png' 


<PlstBtn>: # Dynamically added to ScrollableViewPlaylists
    on_press: 
        print(f"========= Selected playlist: {self.text}")
        app.last_btn_pressed = "plst_btn"
        root.select_playlist()
        app.root.current = 'playlist_videos_screen'

<ChannelBtn>:
    on_press: 
        print(f"++++++++ Selected channel: {self.text}")
        app.last_btn_pressed = "channel_btn"
        root.select_playlist()
        app.root.current = 'channel_videos_screen'

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


class PlaylistVideosHeader(Header):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class YoutubeThumbScreenHeader(Header):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PlaylistsHeader(Header):
    pass


class SubscriptionsHeader(Header):
    pass


class WatchLaterHeader(Header):
    pass


class ChannelVideosHeader(Header):
    pass


class MyChannelsHeader(Header):
    pass


class VideoItem(GridLayout):
    pass


#########################
#  Scrollable views     #
#########################
class ScrollableViewYThumbScreen(ScrollView):
    video_list = ListProperty()

    def __init__(self, client_cmd=b'getthumbnails', **kwargs):
        ''' Send different command to server depending on which button was pressed.
        Cache the list of videos as well for later use.'''
        super().__init__(**kwargs)
        self.client_cmd = client_cmd
        self.channel_cache = False
        print(f"LST BTN {app.last_btn_pressed}")
        print(f"Last screen: {app.last_screen}")
        if app.last_btn_pressed == "ythome" or (app.last_screen == "youtube_thumb_screen" and app.last_btn_pressed == "refresh_button"):
            if app.home_yt_vids_have:
                Logger.info(f"dalYinskiApp: Already have Youtube home videos saved. Retrieving from cache.")
                video_thumb_urls = app.home_yt_vids
                self.video_urls(video_thumb_urls)
            else:
                Logger.info(f"dalYinskiApp: No Youtube home videos cached. Fetching new videos.")
                PlaybackScreen().on_press_go_home()
                time.sleep(1) # wait a bit for the page to load
                self.get_thumbnails(self.client_cmd)
        elif app.last_btn_pressed == "watchlater":
            if app.watch_later_vids_have:
                Logger.info(f"dalYinskiApp: Already have Watch Later videos saved. Retrieving from cache.")
                video_thumb_urls = app.watch_later_vids
                self.video_urls(video_thumb_urls)
            else:
                Logger.info(f"dalYinskiApp: No Watch Later videos cached. Fetching new videos.")
                PlaybackScreen().on_press_watch_later()
                time.sleep(1)
                self.client_cmd = b'getplaylistthumbnails'
                self.get_thumbnails(self.client_cmd)
        elif app.root.current == "playlist_videos_screen":
            # If we cached playlist videos before and the refresh button is pressed, empty
            # the cache and fetch new videos
            if store.exists(app.last_plstname) and app.last_btn_pressed == "refresh_button":
                try:
                    store.delete(app.last_plstname)
                    Logger.info(f"dalYinskiApp: Refreshing playlist videos ||>>{app.last_plstname}<<||.")
                    self.client_cmd = b'getplaylistthumbnails'
                    self.get_thumbnails(self.client_cmd)
                except Exception as e: 
                    Logger.info(f"dalYinskiApp: Exception trying to delete stored playlist videos.")
            # Load playlist videos from settings.json file if we saved it previously 
            elif store.exists(app.last_plstname):
                Logger.info(f"dalYinskiApp: We already have >>{app.last_plstname}<< videos saved. Retrieving from cache.")
                video_thumb_urls = store.get(app.last_plstname)['plstvideos'] # if we opened it previously, get videos from dictionary

                self.video_urls(video_thumb_urls)
            elif not app.plst_videos_dict.get(app.last_plstname) or app.last_btn_pressed == "refresh_button":
                Logger.info(f"dalYinskiApp: No >>{app.last_plstname}<< videos cached. Fetching new videos.")
                time.sleep(1)
                self.client_cmd = b'getplaylistthumbnails'
                self.get_thumbnails(self.client_cmd)
        elif app.last_btn_pressed == "subscriptions":
            if app.subscriptions_vids_have:
                Logger.info(f"dalYinskiApp: Already have Subscriptions videos saved. Retrieving from cache.")
                video_thumb_urls = app.subscriptions_vids
                self.video_urls(video_thumb_urls)
            else:
                Logger.info(f"dalYinskiApp: No Subscriptions videos cached. Fetching new videos.")
                PlaybackScreen().on_press_subscriptions()
                time.sleep(1)
                self.client_cmd = b'getsubscriptionhumbnails'
                self.get_thumbnails(self.client_cmd)
        elif app.root.current == "channel_videos_screen":
            # If we cached channel videos before and the refresh button is pressed, empty
            # the cache and fetch new videos
            if store.exists(app.last_channel) and app.last_btn_pressed == "refresh_button":
                try:
                    store.delete(app.last_channel)
                    Logger.info(f"dalYinskiApp: Refreshing channel videos ||>>{app.last_channel}<<||.")
                    time.sleep(1)
                    self.channel_cache = True
                    self.client_cmd = b'getsubscriptionhumbnails'
                    self.get_thumbnails(self.client_cmd)
                except Exception as e: 
                    Logger.info(f"dalYinskiApp: Exception trying to delete stored channel videos.")
            # Load channel videos from settings.json file if we saved it previously 
            elif store.exists(app.last_channel):
                Logger.info(f"dalYinskiApp: Already have ||>>{app.last_channel}<<|| channel's videos saved. Retrieving from cache.")
                video_thumb_urls = store.get(app.last_channel)['videos']
                self.video_urls(video_thumb_urls)
            elif not app.channel_videos_dict.get(app.last_channel) or app.last_btn_pressed == "refresh_button":
                Logger.info(f"dalYinskiApp: No channel ||>>{app.last_channel}<<|| videos cached. Fetching new videos.")
                time.sleep(1)
                self.channel_cache = True
                self.client_cmd = b'getsubscriptionhumbnails'
                self.get_thumbnails(self.client_cmd)

    def get_thumbnails(self, client_cmd):
        self.t = threading.Thread(target=self._get_thumbnails, args=(client_cmd, ), daemon=True)
        self.t.start()

    def _get_thumbnails(self, client_cmd):
        # print(f">>>>>>>>>>> Client cmd: {client_cmd}")
        # TODO: maybe use a decorator for checking if the server is up, so that it can be reused
        c = DalyinskiClient()
        self.pf = show_popup("Fetching videos... \nPlease wait.")
        self.pf.open()

        video_thumb_urls = c.recv_thumb_list(client_cmd)
        Logger.debug(f"dalYinskiApp: video_thumb_urls {video_thumb_urls}")
        self.video_urls(video_thumb_urls)

        # cache video lists
        if client_cmd == b'getthumbnails':
            app.home_yt_vids = video_thumb_urls
            app.home_yt_vids_have = True
            store.put('home_yt_vids', home_yt_vids=app.home_yt_vids)
        elif self.channel_cache:
            app.channel_videos_dict[app.last_channel] = video_thumb_urls
            store.put(app.last_channel, videos=app.channel_videos_dict[app.last_channel])
        elif client_cmd == b'getplaylistthumbnails' and app.last_btn_pressed == "watchlater":
            app.watch_later_vids = video_thumb_urls
            app.watch_later_vids_have = True
        elif client_cmd == b'getplaylistthumbnails':
            print("CACHING VDS!!!")
            app.plst_videos_dict[app.last_plstname] = video_thumb_urls
            store.put(app.last_plstname, plstvideos=app.plst_videos_dict[app.last_plstname])
        elif client_cmd == b'getsubscriptionhumbnails':
            app.subscriptions_vids = video_thumb_urls
            app.subscriptions_vids_have = True


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
                Logger.debug(f"dalYinskiApp: Video list {self.video_list}")
        except IndexError as e:
            Logger.info(f"dalYinskiApp: {type(e)} {e}")

    
class ScrollableViewPlaylists(ScrollView):
    scroll_view_plst = ObjectProperty()
            
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.width, Window.height)
        self.scroll_view_plst.bind(minimum_height=self.scroll_view_plst.setter('height'))
        # check if have the playlists cached
        if app.usr_playlists_have:
            for plst in app.usr_playlists:
                self.scroll_view_plst.add_widget(PlstBtn(str(plst[1]), text=str(plst[0]))) # plst[1] is playlist link (sent to the constructor in order to open it), plst[0] is playlist name
        else:
            # fetch playlists from server
            self.get_playlists()

    def get_playlists(self):
        t = threading.Thread(target=self._get_playlists, daemon=True)
        t.start()

    def _get_playlists(self):
        c = DalyinskiClient()

        p = show_popup("Fetching playlists... \nPlease wait.")
        p.open()
        app.usr_playlists = c.recv_playlists(b'getplaylists') # a list of tuples of playlist name and link
        app.usr_playlists_have = True
        Logger.debug(f"dalYinskiApp: Got list of playlists: {app.usr_playlists}")
        # Save the playlists to file to load them faster on next app run
        store.put('usr_playlists', usr_playlists=app.usr_playlists)
        Logger.debug(f"dalYinskiApp: Saved {app.usr_playlists} to file.")
        for plst in app.usr_playlists:
            self.scroll_view_plst.add_widget(PlstBtn(str(plst[1]), text=str(plst[0]))) # plst[1] is playlist link (sent to the constructor in order to open it), plst[0] is playlist name
        p.dismiss()

class ScrollableViewMyChannels(ScrollView):
    scroll_view_plst = ObjectProperty()
            
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.width, Window.height)
        self.scroll_view_plst.bind(minimum_height=self.scroll_view_plst.setter('height'))
        # check if have the playlists cached
        if app.my_channels_plst:
            for plst in app.my_channels_plst:
                self.scroll_view_plst.add_widget(ChannelBtn(str(plst[1]), text=str(plst[0]))) # plst[1] is channel link (sent to the constructor in order to open it), plst[0] is channel name
        else:
            # fetch channels from server
            self.get_playlists()

    def get_playlists(self):
        t = threading.Thread(target=self._get_playlists, daemon=True)
        t.start()

    def _get_playlists(self):
        c = DalyinskiClient()

        p = show_popup("Fetching channels... \nPlease wait.")
        p.open()
        app.my_channels_plst = c.recv_playlists(b'getmychplst') # a list of tuples of playlist name and link
        app.my_channels_plst_have = True
        Logger.debug(f"dalYinskiApp: Got list of channels: {app.my_channels_plst}")
        store.put('my_channels_plst', my_channels_plst=app.my_channels_plst)
        Logger.debug(f"dalYinskiApp: Saved {app.my_channels_plst} to file.")
        for plst in app.my_channels_plst:
            self.scroll_view_plst.add_widget(ChannelBtn(str(plst[1]), text=str(plst[0])))
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
    ''' Used by ChannelBtn class below as well. Custom playlist button which receives playlist url
    and the name of the playlist, which is used later as a dict key
    to cache the playlist.'''
    def __init__(self, vidurl, text=''):
        super().__init__(text=text)
        self.vidurl = vidurl
        self.plstname = text

    def select_playlist(self):
        # set the last playlist name and its link each time the button is pressed
        app.last_plstname_link = self.vidurl
        app.last_plstname = self.plstname 
        if app.plst_videos_dict.get(app.last_plstname) and app.last_btn_pressed != "refresh_button":
            # if we previously opened the playlist no need to retrieve it again from server, just use cached one in app.plst_videos_dict
            pass
        else:
            t = threading.Thread(target=self._select_playlist, daemon=True)
            t.start()

    def _select_playlist(self):
        ''' Send playvideo command + video url from the list
        which gets passed in the constructor above as vidurl variable
        so that the server can select that playlist url. '''
        c = DalyinskiClient()
        c.command(b'playvideo' + b' ' + bytes(self.vidurl, 'utf-8'))

class ChannelBtn(Button):
    def __init__(self, vidurl, text=''):
        super().__init__(text=text)
        self.vidurl = vidurl
        self.plstname = text

    def select_playlist(self):
        # set the last playlist name and its link each time the button is pressed
        app.last_channel_link = self.vidurl
        app.last_channel = self.plstname 
        if app.channel_videos_dict.get(app.last_channel) and app.last_btn_pressed != "refresh_button":
            # if we previously opened the playlist no need to retrieve it again from server, just use cached one in app.plstname_dict
            pass
        else:
            t = threading.Thread(target=self._select_playlist, daemon=True)
            t.start()

    def _select_playlist(self):
        c = DalyinskiClient()
        c.command(b'playchannelvideo' + b' ' + bytes(self.vidurl, 'utf-8'))

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
        # set spinner text to empty string so that it doesn't show text under icon
        self.parent.ids.id_start_scr.start_scr_spinner.text = '' 

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
        self.parent.ids.id_start_scr.start_scr_spinner.text = ''


class ReconnectServerScreen(Screen):
    pass


class PlaylistsScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "playlists_screen"
        self.add_widget(PlaylistsHeader())
        self.add_widget(ScrollableViewPlaylists())

    def clear_scroll_view(self):
        self.clear_widgets()


class PlaylistVideosScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        if app.last_screen == "playlists_screen":
            app.last_screen = "playlists_screen"
        else:
            app.last_screen = "playlist_videos_screen"
        self.add_widget(PlaylistVideosHeader())
        self.add_widget(ScrollableViewYThumbScreen())

    def clear_scroll_view(self):
        self.clear_widgets()


class YoutubeThumbScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "youtube_thumb_screen"
        self.add_widget(YoutubeThumbScreenHeader())
        self.add_widget(ScrollableViewYThumbScreen())

    def clear_scroll_view(self):
        self.clear_widgets()


class WatchLaterScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "watchlater_screen"
        self.add_widget(WatchLaterHeader())
        self.add_widget(ScrollableViewYThumbScreen())

    def clear_scroll_view(self):
        self.clear_widgets()


class SubscriptionsScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "subs_screen"
        self.add_widget(SubscriptionsHeader())
        self.add_widget(ScrollableViewYThumbScreen())

    def clear_scroll_view(self):
        self.clear_widgets()


class MyChannelsScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "my_channels_screen"
        self.add_widget(MyChannelsHeader())
        self.add_widget(ScrollableViewMyChannels())

    def clear_scroll_view(self):
        self.clear_widgets()


class ChannelVideosScreen(Screen):
    def add_scroll_view(self):
        Logger.info(f"dalYinskiApp: Current screen: {app.root.current}; Last screen was: {app.last_screen}")
        app.last_screen = "channel_videos_screen"
        self.add_widget(ChannelVideosHeader())
        self.add_widget(ScrollableViewYThumbScreen())

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

    # Check if we stored the playlists previously in a file
    if store.exists('usr_playlists'):
        usr_playlists_have = True
        usr_playlists = store.get('usr_playlists')['usr_playlists']
    else:
        usr_playlists = []
        usr_playlists_have = False

    # if store.exists('my_channels_plst'):
    #     my_channels_plst_have = True
    #     my_channels_plst = store.get('my_channels_plst')['my_channels_plst']
    # else:
    #     my_channels_plst = []
    #     my_channels_plst_have = False

    last_plstname = None
    last_plstname_link = None
    plst_videos_dict = {}

    if store.exists('home_yt_vids'):
        home_yt_vids_have = True
        home_yt_vids = store.get('home_yt_vids')['home_yt_vids']
    else:
        home_yt_vids = []
        home_yt_vids_have = False

    watch_later_vids = []
    watch_later_vids_have = False

    subscriptions_vids = []
    subscriptions_vids_have = False


    if store.exists('my_channels_plst'):
        my_channels_plst_have = True
        my_channels_plst = store.get('my_channels_plst')['my_channels_plst']
    else:
        my_channels_plst = []
        my_channels_plst_have = False

    last_channel = None
    last_channel_link = None
    channel_videos_dict = {}

    def refresh_vids(self, where=None):
        ''' Clear the old list of videos, then clear the widgets of current screen
        and trigger the ScrollableViewYThumbScreen again to repopulate the screen
        with new videos. Stupid. Works.'''
        Logger.info(f"dalYinskiApp: Clearing playlist and refreshing...")
        if where == "ythome":
            app.home_yt_vids_have = False
            app.home_yt_vids = []
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'youtube_thumb_screen'
        elif where == "playlists":
            app.usr_playlists_have = False
            app.usr_playlists = []
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'playlists_screen'
        elif where == "playlist_thumbs":
            # Go to playlist in the browser again to refresh the page
            PlstBtn(app.last_plstname_link, text=str(app.last_plstname)).select_playlist()
            app.plst_videos_dict[app.last_plstname] = None
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'playlist_videos_screen'
        elif where == "watch_later":
            app.watch_later_vids_have = False
            app.watch_later_vids = []
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'watchlater_screen'
        elif where == "subscriptions":
            app.subscriptions_vids_have = False
            app.subscriptions_vids = []
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'subs_screen'
        elif where == "channel_thumbs":
            ChannelBtn(app.last_channel_link, text=str(app.last_channel)).select_playlist()
            app.channel_videos_dict[app.last_channel] = None
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'channel_videos_screen'
        elif where == "my_channels":
            print(f"### Last channnel ### {app.last_channel}")
            app.my_channels_plst_have = False
            app.my_channels_plst = []
            app.root.current_screen.clear_scroll_view()
            app.root.current = 'start_screen'
            app.root.current = 'my_channels_screen'

    def open_settings(self, *largs):
            pass

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
