#!/usr/bin/env python3

import wx
from dalyinski.server.gui import WinFrame

if __name__=="__main__":
    app = wx.App()
    win = WinFrame()
    app.MainLoop()

