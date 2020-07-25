#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

# local imports
from .client import RemofoyClient

class MainApp(App):
    def build(self):
        # TODO: add icon to app
        main_layout = BoxLayout(orientation='vertical',
                                spacing=5)

        btn_ping = Button(text='Send ping',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_ping.bind(on_press=self.on_press_send_ping)
        

        btn_open_browser = Button(text='Open Firefox',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(1,.30,.30,1))
        btn_open_browser.bind(on_press=self.on_press_open_browser)


        btn_watch_later = Button(text='Watch later',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_watch_later.bind(on_press=self.on_press_watch_later)

        btn_play_pause = Button(text='Play/Pause',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_play_pause.bind(on_press=self.on_press_play_pause)
        
        btn_play_next = Button(text='Play Next',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_play_next.bind(on_press=self.on_press_play_next)
        
        btn_go_home = Button(text='Go Home',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_go_home.bind(on_press=self.on_press_go_home)
        
        btn_fullscreen = Button(text='Fullscreen',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5},
                background_color=(0,1,0,1))
        btn_fullscreen.bind(on_press=self.on_press_fullscreen)
        
        main_layout.add_widget(btn_ping)
        main_layout.add_widget(btn_open_browser)
        main_layout.add_widget(btn_watch_later)
        main_layout.add_widget(btn_play_pause)
        main_layout.add_widget(btn_go_home)
        main_layout.add_widget(btn_play_next)
        main_layout.add_widget(btn_fullscreen)

        return main_layout

    def on_press_open_browser(self, instance):
        c = RemofoyClient()
        c.command(b'fbro')

    def on_press_send_ping(self, instance):
        c = RemofoyClient()
        c.command(b'ping')

    def on_press_play_pause(self, instance):
        c = RemofoyClient()
        c.command(b'playpause')

    def on_press_watch_later(self, instance):
        c = RemofoyClient()
        c.command(b'watchlater')

    def on_press_go_home(self, instance):
        c = RemofoyClient()
        c.command(b'gohome')

    def on_press_play_next(self, instance):
        c = RemofoyClient()
        c.command(b'playnext')

    def on_press_fullscreen(self, instance):
        c = RemofoyClient()
        c.command(b'fullscreen')

if __name__ == '__main__':

    app = MainApp()
    app.run()
