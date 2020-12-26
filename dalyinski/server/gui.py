#!/usr/bin/env python3

__version__ = '0.6'

import wx
import wx.adv

from dalyinski.server.server import ServerConn

class WinFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="dalYinski server", size=(210, 150))
        status_bar = self.CreateStatusBar(style=wx.STB_DEFAULT_STYLE, id=-1, name="statusbar")
        status_bar.SetStatusText(f"GUI version: {__version__}")

        self.server = ServerConn()

        panel = wx.Panel(self)
        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(vert_sizer)

        start_srv_btn = wx.Button(panel, label="Start server and open browser", pos=(10, 10))
        start_srv_btn.Bind(wx.EVT_BUTTON, self.run_server)

        quit_btn = wx.Button(panel, label="Quit", pos=(10, 50))
        quit_btn.Bind(wx.EVT_BUTTON, self.quit)

        vert_sizer.Add(start_srv_btn, 0, wx.ALL | wx.EXPAND, 5)
        vert_sizer.Add(quit_btn, 0, wx.ALL | wx.EXPAND, 5)

        self.Show()

    def run_server(self, event):
        busy = wx.BusyCursor()
        self.server.run()
        notification = wx.adv.NotificationMessage("dalYinski server", message="Opening browser").Show()
        self.server.open_browser()
        del busy


    def quit(self, event):
        self.server.close_browser()
        self.Destroy()
    
        
if __name__=="__main__":
    app = wx.App()
    frame = WinFrame()
    app.MainLoop()
