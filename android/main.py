#!/usr/bin/env python3

__version__ = '0.8'

import threading

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
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

# local imports
from client import DalyinskiClient

# variables for correct display of either play or pause button
isPaused = True
last_cmd = ''

Builder.load_string("""
<DalyinskiScrMgr>:
    StartScreen:
    YoutubeThumbScreen:
        id: yt_th_scr
    PlaybackScreen:
        id: play_scr

<PlaybackScreen>:
    name: 'playback_screen'

    btn_play_pause: btn_play_pause

    canvas.before:
        Rectangle:
            size: self.size
            pos: self.pos
            source: './img/background.png'
    BoxLayout:
        id: main_layout
        orientation: 'vertical'
        spacing: 2
        padding: 5
        BoxLayout:
            orientation: 'horizontal'
            Button:
                text: 'Start screen'
                on_release: 
                    root.manager.current = 'start_screen'
                    root.manager.transition.direction = 'right'
            Button:
                id: btn_open_browser
                text: 'Connect to server and open browser'
                text_size: (100, None)
                on_press: root.on_press_open_browser()
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
                on_press: root.on_press_switch_tab()
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
                source: './img/baseline_home_black_48.png' if self.state == 'normal' else './img/outline_home_black_48.png'
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
            
            
    

<StartScreen>:
    name: 'start_screen'
    container: container
    id: container
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Youtube Home'
            background_color: (1, 0, 0, 1)
            on_press: 
                root.manager.current = 'show_imgs' 
                root.manager.transition.direction = 'left'
        Button:
            text: 'Playback'
            on_press: 
                root.manager.current = 'playback_screen' 
                root.manager.transition.direction = 'left'

<YoutubeThumbScreen>:
    name: 'show_imgs'
    prop_show_imgs: prop_show_imgs
    on_pre_enter: root.add_lacuna()

    GridLayout:
        id: prop_show_imgs
        cols: 3
        Button:
            text: 'Start screen'
            on_press:
                root.manager.current = 'start_screen' 
                root.manager.transition.direction = 'right'
            
        Button:
            text: 'Add image'
            on_press: root.add_lacuna()
            size_hint: 1, 0.1
    

<ThumbLayout>:
    prop_thumb_lyt_ai: prop_thumb_lyt_ai
    prop_thumb_lyt_label: prop_thumb_lyt_label
    BoxLayout:
        orientation: 'vertical'
        AsyncImage:
            id: prop_thumb_lyt_ai
            center: self.parent.center
            size: self.parent.width, self.parent.height
        Label:
            id: prop_thumb_lyt_label
            size_hint: 1, 0.1
        Button:
            on_press: 
                app.root.current = 'start_screen'
            text: 'Play video'
            size_hint: 1, 0.3


""")

video_thumb_urls = [
    'https://i.ytimg.com/vi/Bzty7HDJu4Y/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLBLaPX7QFRoumLRHQdQzqOqimQSzw',
    'https://i.ytimg.com/vi/USXHxgWoS9g/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLBpSXXRzSrsOLox5p2ejDfUDWSeBg',
    'https://i.ytimg.com/vi/59Ny29nNh2A/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLBZc-L22bp2mCDkUShxTSQ7J_p7qw',
    'https://i.ytimg.com/vi/paQsE53YkVU/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLBvevKpyxxh6BJ_SoGTcQJByd4a5g',
    'https://i.ytimg.com/vi/36X4hwsvjJE/hq720.jpg?sqp=-oaymwEZCNAFEJQDSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLCE8VcrwjmpSfBZaZZ8ZgZBLKVbZw',
    'https://i.ytimg.com/vi/v7NUi88Lxi8/hq720.jpg?sqp=-oaymwEZCNAFEJQDSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLC4bbrj3ISvkpMht9zQgesiF7sw9g',
    'https://i.ytimg.com/vi/paQsE53YkVU/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLBvevKpyxxh6BJ_SoGTcQJByd4a5g',
    'https://i.ytimg.com/vi/36X4hwsvjJE/hq720.jpg?sqp=-oaymwEZCNAFEJQDSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLCE8VcrwjmpSfBZaZZ8ZgZBLKVbZw',
    'https://i.ytimg.com/vi/v7NUi88Lxi8/hq720.jpg?sqp=-oaymwEZCNAFEJQDSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLC4bbrj3ISvkpMht9zQgesiF7sw9g'
        ]


#########################
# Custom button classes #
#########################
class ThumbLayout(BoxLayout):
    prop_thumb_lyt_ai = ObjectProperty()
    prop_thumb_lyt_label = ObjectProperty()

    def __init__(self, imgsrc, labeltext, **kwargs):
        super().__init__(**kwargs)
        self.prop_thumb_lyt_ai.source = imgsrc
        self.prop_thumb_lyt_label.text = labeltext
            

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
        # print('PlayPause ==>',isPaused)


###########
# Screens #
###########
class YoutubeThumbScreen(Screen):
    grid_si_prop = ObjectProperty()

    def add_lacuna(self):
        for thumb in video_thumb_urls:
            self.prop_show_imgs.add_widget(ThumbLayout(thumb, 'heioha'))

    def get_thumbnails(self):
        c = DalyinskiClient()
        c.command(b'getthumbnails')
        for thumb in video_thumb_urls:
            self.prop_show_imgs.add_widget(ThumbLayout(thumb, 'heioha'))

class StartScreen(Screen):
    pass


class PlaybackScreen(Screen):
    btn_play_pause = ObjectProperty()

    ############################
    # PlaybackScreen Callbacks #
    ############################
    def show_popup(self, message='Info'):
        self.popup = Popup(title='Info',
            content=Label(text=message),
            size_hint=(0.8, 0.8), size=(600, 400),
            auto_dismiss=False)
        return self.popup

    # TODO: maybe use a singleton instead of instantiating new class in every call
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    def _on_press_open_browser(self):
        ''' Private function to call with threading, to prevent gui blocking '''
        p = self.show_popup('Connecting to server\nand opening web browser...\nPlease wait.')
        p.open()
        c = DalyinskiClient()
        c.command(b'fbro')
        p.dismiss()

    def on_press_open_browser(self):
        ''' Threading function to call the "real" function '''
        t = threading.Thread(target=self._on_press_open_browser, args=())
        t.start()

    def on_press_play_previous(self):
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
        pass
        # c = DalyinskiClient()
        # c.command(b'scrollup')

class DalyinskiScrMgr(ScreenManager):
    pass

class MainApp(App):
    title = "DalYinski"

    def build(self):
        screen_mgr = DalyinskiScrMgr()
        screen_mgr.current = 'start_screen'
        return screen_mgr
      
if __name__ == '__main__':
    app = MainApp()
    app.run()
