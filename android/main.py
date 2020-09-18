#!/usr/bin/env python3

__version__ = '0.7'

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
                                spacing=2,
                                padding=5)
        cpt_tab_home_lyt = BoxLayout(orientation='horizontal',
                                        spacing=2)
        playback_btns_lyt = BoxLayout(orientation='horizontal',
                                        spacing=1)
        ff_rewind_btns_lyt = BoxLayout(orientation='horizontal',
                                        spacing=1)
        thumb_btns_lyt = BoxLayout(orientation='horizontal',
                                        spacing=1)

        # This will only draw a rectangle at the layout’s initial position and size.
        # To make sure the rect is drawn inside the layout, when the layout size/pos changes, we need to listen to any changes and update the rectangles size and pos.
        with main_layout.canvas.before:
            self.rect = Rectangle(size=main_layout.size,
                                  pos=main_layout.pos,
                                  source='./data/background.png')
        main_layout.bind(size=self._update_rect, pos=self._update_rect)



        btn_next_thumb = Button(text='Next thumbnail vid',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_next_thumb.bind(on_press=self.on_press_next_thumb)

        btn_prev_thumb = Button(text='Previous thumbnail vid',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_prev_thumb.bind(on_press=self.on_press_prev_thumb)

        btn_scroll_down = Button(text='Scroll down',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_scroll_down.bind(on_press=self.on_press_scroll_down)

        btn_scroll_up = Button(text='Scroll up',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_scroll_up.bind(on_press=self.on_press_scroll_up)

        btn_select_thumb = Button(text='Select video',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_select_thumb.bind(on_press=self.on_press_select_thumb)

        btn_open_browser = Button(text='Open Firefox',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_open_browser.bind(on_press=self.on_press_open_browser)

        btn_watch_later = Button(text='Watch later',
                size_hint=(0.9, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_watch_later.bind(on_press=self.on_press_watch_later)

        btn_play_previous = Button(text='Play Previous', 
                size_hint=(0.4, 0.95),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_play_previous.bind(on_press=self.on_press_play_previous)

        btn_play_pause = Button(text='Play/Pause',
                size_hint=(0.8, 1),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_play_pause.bind(on_press=self.on_press_play_pause)
        
        btn_play_next = Button(text='Play Next',
                size_hint=(0.4, 0.95),
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

        btn_rewind = Button(text='Rewind', 
                size_hint=(0.4, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_rewind.bind(on_press=self.on_press_rewind)

        btn_fforward = Button(text='Fast forward', 
                size_hint=(0.4, 0.8),
                pos_hint={'center_x': .5, 'center_y': .5})
        btn_fforward.bind(on_press=self.on_press_fforward)

        playback_btns_lyt.add_widget(btn_play_previous)
        playback_btns_lyt.add_widget(btn_play_pause)
        playback_btns_lyt.add_widget(btn_play_next)

        ff_rewind_btns_lyt.add_widget(btn_rewind)
        ff_rewind_btns_lyt.add_widget(btn_fforward)

        cpt_tab_home_lyt.add_widget(btn_captions)
        cpt_tab_home_lyt.add_widget(btn_go_home)
        cpt_tab_home_lyt.add_widget(btn_switch_tab)

        thumb_btns_lyt.add_widget(btn_next_thumb)
        thumb_btns_lyt.add_widget(btn_select_thumb)
        thumb_btns_lyt.add_widget(btn_prev_thumb)
        thumb_btns_lyt.add_widget(btn_scroll_down)
        thumb_btns_lyt.add_widget(btn_scroll_up)
        
        main_layout.add_widget(btn_open_browser)
        main_layout.add_widget(btn_watch_later)
        main_layout.add_widget(thumb_btns_lyt)
        main_layout.add_widget(cpt_tab_home_lyt)

        # playback buttons
        main_layout.add_widget(playback_btns_lyt)
        main_layout.add_widget(ff_rewind_btns_lyt)

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

    # TODO: maybe use a singleton instead of instantiating new class in every call
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    def _on_press_open_browser(self, instance):
        ''' Private function to call with threading, to prevent gui blocking '''
        p = self.show_popup('Connecting to server\nand opening web browser...\nPlease wait.')
        p.open()
        c = DalyinskiClient()
        c.command(b'fbro')
        p.dismiss()

    def on_press_open_browser(self, instance):
        ''' Threading function to call the "real" function '''
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

    def on_press_fforward(self, instance):
        c = DalyinskiClient()
        c.command(b'fforward')

    def on_press_rewind(self, instance):
        c = DalyinskiClient()
        c.command(b'rewind')

    def on_press_next_thumb(self, instance):
        c = DalyinskiClient()
        c.command(b'nextthumb')

    def on_press_prev_thumb(self, instance):
        c = DalyinskiClient()
        c.command(b'prevthumb')

    def on_press_select_thumb(self, instance):
        c = DalyinskiClient()
        c.command(b'selectthumb')

    def on_press_scroll_down(self, instance):
        c = DalyinskiClient()
        c.command(b'scrolldown')

    def on_press_scroll_up(self, instance):
        c = DalyinskiClient()
        c.command(b'scrollup')

if __name__ == '__main__':
    app = MainApp()
    app.run()
