import wx

class InfoFrame(wx.Frame):
    ''' Used for showing various information to user. '''
    def __init__(self):
        super().__init__(parent=None, title="INFO - dalYinski server", size=(210, 150))
        panel = wx.Panel(self)

        info_win = wx.MessageDialog(panel, "Looks like you didn't create separate Firefox profile.\n Please create it first.")

        with info_win as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.Destroy()
            else:
                pass


