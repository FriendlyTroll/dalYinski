#!/usr/bin/env python3

__version__ = '0.4'

import threading

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle

# local imports
from client import DalyinskiClient


class MainApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical',
                                spacing=2)
        cpt_tab_home_lyt = BoxLayout(orientation='horizontal',
                                        spacing=2)
        playback_btns_lyt = BoxLayout(orientation='horizontal',
                                        spacing=2)


        # This will only draw a rectangle at the layout’s initial position and size.
        # To make sure the rect is drawn inside the layout, when the layout size/pos changes, we need to listen to any changes and update the rectangles size and pos.
        with main_layout.canvas.before:
            self.rect = Rectangle(size=main_layout.size,
                                  pos=main_layout.pos,
                                  source='./data/background.png')
        main_layout.bind(size=self._update_rect, pos=self._update_rect)



        btn_ping = Button(text='Connect to server',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_ping.bind(on_press=self.on_press_send_ping)
        

        btn_open_browser = Button(text='Open Firefox',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_open_browser.bind(on_press=self.on_press_open_browser)

        btn_watch_later = Button(text='Watch later',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_watch_later.bind(on_press=self.on_press_watch_later)

        btn_play_previous = Button(text='Play Previous', 
                size_hint=(0.4, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_play_previous.bind(on_press=self.on_press_play_previous)

        btn_play_pause = Button(text='Play/Pause',
                size_hint=(0.8, 1),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_play_pause.bind(on_press=self.on_press_play_pause)
        
        btn_play_next = Button(text='Play Next',
                size_hint=(0.4, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_play_next.bind(on_press=self.on_press_play_next)
        
        btn_go_home = Button(text='Go Home',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_go_home.bind(on_press=self.on_press_go_home)
        
        btn_fullscreen = Button(text='Fullscreen',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_fullscreen.bind(on_press=self.on_press_fullscreen)

        btn_captions = Button(text='Captions On/off',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_captions.bind(on_press=self.on_press_captions)

        btn_switch_tab = Button(text='Switch tab',
                size_hint=(0.8, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_switch_tab.bind(on_press=self.on_press_switch_tab)

        playback_btns_lyt.add_widget(btn_play_previous)
        playback_btns_lyt.add_widget(btn_play_pause)
        playback_btns_lyt.add_widget(btn_play_next)

        cpt_tab_home_lyt.add_widget(btn_captions)
        cpt_tab_home_lyt.add_widget(btn_go_home)
        cpt_tab_home_lyt.add_widget(btn_switch_tab)
        
        main_layout.add_widget(btn_ping)
        main_layout.add_widget(btn_open_browser)
        main_layout.add_widget(btn_watch_later)
        main_layout.add_widget(cpt_tab_home_lyt)

        # playback buttons
        main_layout.add_widget(playback_btns_lyt)
        main_layout.add_widget(btn_fullscreen)

        
        return main_layout

    
    def _update_rect(self, instance, value):
        ''' Update rectangle position for drawing background '''
        self.rect.pos = instance.pos
        self.rect.size = instance.size


    def show_popup(self, message='Info'):
        self.popup = Popup(title='Info',
            content=Label(text=message),
            size_hint=(0.8, 0.8), size=(600, 400),
            auto_dismiss=False)
        return self.popup

    def _on_press_send_ping(self, instance):
        ''' Private function to call with threading, to prevent gui blocking '''
        p = self.show_popup('Discovering server.\nPlease wait...')
        p.open() # Open the popup
        c = DalyinskiClient()
        c.command(b'ping')
        p.dismiss() # Close popup after we send the inital ping packet

    def on_press_send_ping(self, instance):
        ''' Threading function to call the "real" function '''
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

    def on_press_play_previous(self, instance):
        c = DalyinskiClient()
        c.command(b'playprevious')

    def on_press_play_pause(self, instance):
        c = DalyinskiClient()
        c.command(b'playpause')

    def on_press_play_next(self, instance):
        c = DalyinskiClient()
        c.command(b'playnext')

    def on_press_watch_later(self, instance):
        c = DalyinskiClient()
        c.command(b'watchlater')

    def on_press_go_home(self, instance):
        c = DalyinskiClient()
        c.command(b'gohome')

    def on_press_fullscreen(self, instance):
        c = DalyinskiClient()
        c.command(b'fullscreen')

    def on_press_captions(self, instance):
        c = DalyinskiClient()
        c.command(b'captions')

    def on_press_switch_tab(self, instance):
        c = DalyinskiClient()
        c.command(b'switchtab')

if __name__ == '__main__':
    app = MainApp()
    app.run()
