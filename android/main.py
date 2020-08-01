#!/usr/bin/env python3

__version__ = '0.2'

import threading

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup

# local imports
from client import DalyinskiClient

class MainApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical',
                                spacing=5)
        horizontal_layout_1 = BoxLayout(orientation='horizontal',
                                        spacing=5)

        btn_ping = Button(text='Connect to server',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
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

        btn_captions = Button(text='Closed captions On/off',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_captions.bind(on_press=self.on_press_captions)

        horizontal_layout_1.add_widget(btn_captions)
        horizontal_layout_1.add_widget(btn_go_home)
        
        main_layout.add_widget(btn_ping)
        main_layout.add_widget(btn_open_browser)
        main_layout.add_widget(btn_watch_later)
        main_layout.add_widget(btn_play_pause)
        main_layout.add_widget(horizontal_layout_1)
        main_layout.add_widget(btn_play_next)
        main_layout.add_widget(btn_fullscreen)

        
        return main_layout

    def show_popup(self, message='Info'):
        self.popup = Popup(title='Info',
            content=Label(text=message),
            size_hint=(None, None), size=(400, 200),
            auto_dismiss=False)
        return self.popup

    # private function to call with threading, to prevent gui blocking
    def _on_press_send_ping(self, instance):
        p = self.show_popup('Discovering server.\nPlease wait...')
        p.open() # Open the popup
        c = DalyinskiClient()
        c.command(b'ping')
        p.dismiss() # Close popup after we send the inital ping packet

    # threading function to call the "real" function
    def on_press_send_ping(self, instance):
        t = threading.Thread(target=self._on_press_send_ping, args=(instance,))
        t.start()

    def _on_press_open_browser(self, instance):
        p = self.show_popup('Opening web browser...')
        p.open()
        c = DalyinskiClient()
        c.command(b'fbro')
        p.dismiss()

    def on_press_open_browser(self, instance):
        t = threading.Thread(target=self._on_press_open_browser, args=(instance,))
        t.start()

    def on_press_play_pause(self, instance):
        c = DalyinskiClient()
        c.command(b'playpause')

    def on_press_watch_later(self, instance):
        c = DalyinskiClient()
        c.command(b'watchlater')

    def on_press_go_home(self, instance):
        c = DalyinskiClient()
        c.command(b'gohome')

    def on_press_play_next(self, instance):
        c = DalyinskiClient()
        c.command(b'playnext')

    def on_press_fullscreen(self, instance):
        c = DalyinskiClient()
        c.command(b'fullscreen')

    def on_press_captions(self, instance):
        c = DalyinskiClient()
        c.command(b'captions')

if __name__ == '__main__':
    app = MainApp()
    app.run()
