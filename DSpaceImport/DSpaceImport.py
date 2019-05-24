# classes for the ui
import wx
import configparser
from pathlib import Path

class LogonDialog(wx.Dialog):
    def __init__(self, config):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('logonDialogTitle','Login'))
        self.loginCookie = None
        self.loggedIn = False

        # input boxes for username and password
        # email row
        emailRowSizer = wx.BoxSizer(wx.VERTICAL)
        emailLabel = wx.StaticText(self, label=labels.get('logonDialogUsername','Username'))
        emailRowSizer.Add(emailLabel, 0, wx.ALL, 5)
        self.email = wx.TextCtrl(self)
        emailRowSizer.Add(self.email, 0, wx.ALL, 5)
        # password row
        passwordRowSizer = wx.BoxSizer(wx.VERTICAL)
        passwordLabel = wx.StaticText(self, label=labels.get('logonDialogPassword','Password'))
        passwordRowSizer.Add(passwordLabel, 0, wx.ALL, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.onLogin)
        passwordRowSizer.Add(self.password, 0, wx.ALL, 5)

        dialogSizer = wx.BoxSizer(wx.VERTICAL)
        dialogSizer.Add(emailRowSizer, 0, wx.ALL, 5)
        dialogSizer.Add(passwordRowSizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label=labels.get('logonDialogLoginButton','Submit'))
        btn.Bind(wx.EVT_BUTTON, self.onLogin)
        dialogSizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(dialogSizer)
        self.Layout()

    def onLogin(self, event):
        # get 
        # logon successful
        self.loggedIn = True
        self.Close()

class MappingDialog(wx.Dialog):
    def __init__(self, config):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('mappingDialogTitle','Mapping'))



class ImportPanel(wx.Panel):
    def __init__(self, parent, authenticated, authCookie, config):
        super().__init__(parent)
        labels = config['Labels']
        self.config = config
        self.authenticated = authenticated
        self.authCookie = authCookie
        self.mappingDict = {}
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(wx.StaticText(self, label=labels.get('mainPanelDescription','')), 0, wx.ALL, 5)

        # select excel file row
        excelRowSizer = wx.BoxSizer(wx.VERTICAL)
        excelRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelFilePickerLabel','Select file')), 0, wx.ALL, 5)
        self.excelPicker = wx.FilePickerCtrl(self, size=(-1, 25), wildcard=self.config['FileTypeWildcard']['fileImportWildcard'])
        excelRowSizer.Add(self.excelPicker, 0, wx.ALL, 5)
        mainSizer.Add(excelRowSizer)
        mainSizer.AddSpacer(30)

        # mapping button
        mappingRowSizer = wx.BoxSizer(wx.VERTICAL)
        mappingRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelMappingDescription','Mapping setup')), 0, wx.ALL, 5)
        mappingRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelMappingFilePickerLabel','Select mapping file')), 0, wx.ALL, 5)
        self.mappingPicker = wx.FilePickerCtrl(self, size=(-1, 25), wildcard=self.config['FileTypeWildcard']['mapFileWildcard'])
        #add an event to this and process the file opened
        self.mappingPicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.mappingSelected)
        mappingRowSizer.Add(self.mappingPicker, 0, wx.ALL, 5)
        self.mappingButton = wx.Button(self, label=labels.get('mainPanelMappingSetupButton','Setup mapping'))
        self.mappingButton.Bind(wx.EVT_BUTTON, self.showMappingDialog)
        mappingRowSizer.Add(self.mappingButton, 0, wx.ALL, 5)

        mainSizer.Add(mappingRowSizer)
        mainSizer.AddSpacer(30)

        # collection select

        # button to import

        self.SetSizer(mainSizer)

    def mappingSelected(self, event):
        self.fileName = Path((self.mappingPicker.GetPath()).replace('\\', '/'))
        print(self.fileName)
        mapping = configparser.ConfigParser()
        mapping.read(self.fileName)
        print(mapping.sections())
        for key in mapping[self.config['Mapping']['mappingSectionName']]:
            if key not in self.mappingDict:
                self.mappingDict[key] = mapping[self.config['Mapping']['mappingSectionName']][key]
        print(self.mappingDict)


    def showMappingDialog(self, event):
        print("open mapping dialog")

class ImportFrame(wx.Frame):
    def __init__(self, config):
        labels = config['Labels']
        super().__init__(None, title=labels.get('appMainTitle','Import'), size=(300, 500))

        with LogonDialog(config) as logonDlg:
            logonDlg.ShowModal()
            self.authenticated = logonDlg.loggedIn
            self.authCookie = logonDlg.loginCookie
            if not self.authenticated:
                self.Close()

        print (self.authenticated)
        panel = ImportPanel(self, self.authenticated, self.authCookie, config)
        self.Show()


if __name__ == '__main__':
    # load config
    config = configparser.ConfigParser(empty_lines_in_values=False)
    config.read('config.ini')
    print(config.sections())
    app = wx.App(False)
    frame = ImportFrame(config)
    app.MainLoop()