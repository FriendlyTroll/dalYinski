#!/usr/bin/env python3

__version__ = '0.4'

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Notify

from dalyinski.server.server import ServerConn


class Win (Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("dalYinski server")
        self.connect("delete-event", self.delete_event)
        # create a virtical box to hold some widgets
        vbox = Gtk.VBox(False)

        # make a startserver button
        startserver = Gtk.Button("Start server")
        startserver.connect("clicked",self.run_server)

        # make a quit button
        quit_btn = Gtk.Button("Quit")
        quit_btn.connect("clicked",self.quit)

        # add the startserver to the vbox
        vbox.pack_start(startserver, expand=True, fill=True, padding=0)
        vbox.pack_start(quit_btn, expand=True, fill=True, padding=0)
        # create a label and add to the vbox
        label=Gtk.Label("Server GUI for dalYinski")
        version_label=Gtk.Label(f'GUI version: {__version__}')
        vbox.pack_start(label, expand=True, fill=True, padding=0)
        vbox.pack_start(version_label, expand=True, fill=True, padding=0)
        #add the vbox to the Window
        self.add(vbox)
        #show all of the stuff
        self.show_all()
        #make a status icon
        self.statusicon = Gtk.StatusIcon.new_from_file('/usr/share/pixmaps/dalyinski-server.png')
        self.statusicon.connect('activate', self.status_clicked )
        self.statusicon.set_tooltip_text("The server is NOT running.")
        self.server = ServerConn()

        #start the Gtk main loop
        Gtk.main()
    
    def run_server(self, button):
        self.server.run()
        # set tooltip
        self.statusicon.set_tooltip_text("The server is running.")

        # show a notification as well
        Notify.init('dalYinski server')
        noticon = Notify.Notification.new('dalYinski server', 'Server started', '/usr/share/pixmaps/dalyinski-server.png')
        noticon.show()

    def quit(self,button):
        #quit the Gtk main loop
        Gtk.main_quit()

    
    def delete_event(self,window,event):
        #don't delete; hide instead
        self.hide_on_delete()
        self.statusicon.set_tooltip_text("the window is hidden")
        return True
        
    def status_clicked(self,status):
        #unhide the window
        self.show_all()
        # self.statusicon.set_tooltip_text("the window is visible")
        
if __name__=="__main__":
    win = Win()
