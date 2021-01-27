import wx

class InfoFrame(wx.Frame):
    ''' Used for showing various information to user. '''
    def __init__(self, text):
        super().__init__(parent=None, title="INFO - dalYinski server", size=(210, 150))
        panel = wx.Panel(self)

        info_win = wx.MessageDialog(panel, text)

        with info_win as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.Destroy()
            else:
                pass


