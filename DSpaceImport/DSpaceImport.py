# classes for the ui
import wx
import wx.grid as gridlib
import configparser
from pathlib import Path

from DataObjects import Mapping

class LogonDialog(wx.Dialog):
    def __init__(self, config):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('logonDialogTitle','Login'))
        self.loginCookie = None
        self.loggedIn = False

        # input boxes for username and password
        # email row
        emailRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        emailLabel = wx.StaticText(self, label=labels.get('logonDialogUsername','Username'))
        emailRowSizer.Add(emailLabel, 0, wx.ALL, 5)
        self.email = wx.TextCtrl(self)
        emailRowSizer.Add(self.email, 0, wx.ALL, 5)
        # password row
        passwordRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        passwordLabel = wx.StaticText(self, label=labels.get('logonDialogPassword','Password'))
        passwordRowSizer.Add(passwordLabel, 0, wx.ALL, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        passwordRowSizer.Add(self.password, 0, wx.ALL, 5)

        dialogSizer = wx.BoxSizer(wx.VERTICAL)
        dialogSizer.Add(emailRowSizer, 0, wx.ALL, 5)
        dialogSizer.Add(passwordRowSizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label=labels.get('logonDialogLoginButton','Submit'))
        btn.Bind(wx.EVT_BUTTON, self.on_login)
        dialogSizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(dialogSizer)
        self.Layout()
        self.Fit()

    def on_login(self, event):
        # get 
        # logon successful
        self.loggedIn = True
        self.Close()


class MappingDialog(wx.Dialog):
    def __init__(self, config, mappingData, fileName):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('mappingDialogTitle','Mapping'))
        self.mappingData = mappingData
        self.fileName = fileName
        self.config = config

        print(self.mappingData)
        print(self.fileName)

        self.mappingListCtrl = gridlib.Grid(self)
        self.mappingListCtrl.CreateGrid(numRows=len(mappingData)+int(config['Mapping']['mappingNumberOfRows']), numCols=2)
        self.mappingListCtrl.SetColLabelValue(0, labels.get('mappingControlFileColumnLabel', 'Column'))
        self.mappingListCtrl.SetColLabelValue(1, labels.get('mappingControlMetadataFieldLabel', 'Field'))
        self.mappingListCtrl.SetColSize(0, -1)
        self.mappingListCtrl.SetColSize(1, -1)

        index = 0
        for key,val in mappingData.items():
            self.mappingListCtrl.SetCellValue(index, 0, val.colName)
            self.mappingListCtrl.SetCellValue(index, 1, val.metadataField)
            index =+ 1

        dialogSizer = wx.BoxSizer(wx.VERTICAL)
        dialogSizer.Add(self.mappingListCtrl, 0, wx.ALL|wx.EXPAND, 5)
        saveButton = wx.Button(self, label=labels.get('mappingDialogSaveButton','Save'))
        saveButton.Bind(wx.EVT_BUTTON, self.save_mapping)
        dialogSizer.AddSpacer(10)
        dialogSizer.Add(saveButton, 0, wx.ALL, 5)
        self.SetSizer(dialogSizer)
        self.Fit()

    def save_mapping(self, event):
        print("save button clicked")
        self.mappingData.clear()
        _newMapping = configparser.ConfigParser()
        _newMapping.add_section(self.config['Mapping']['mappingSectionName'])
        for index in range(0,self.mappingListCtrl.GetNumberRows()):
            if len(self.mappingListCtrl.GetCellValue(index, 0)) > 0 and len(self.mappingListCtrl.GetCellValue(index, 1)) > 0:
                row = Mapping(self.mappingListCtrl.GetCellValue(index, 0), self.mappingListCtrl.GetCellValue(index, 1))
                self.mappingData[row.id] = row
                _newMapping.set(self.config['Mapping']['mappingSectionName'], row.colName, row.metadataField)
        # prompt user to save the mapping 
        with wx.FileDialog(self, message="Save file as ...", defaultFile=(self.fileName.name if len(self.fileName) > 0 else ""), wildcard=self.config['FileTypeWildcard']['mapFileWildcard'], style=wx.FD_SAVE) as saveDialog:
            if saveDialog.ShowModal() == wx.ID_OK:
                path = Path((saveDialog.GetPath()).replace('\\', '/'))
                # write the file
                try:
                    with open(path, "wt") as file:
                        _newMapping.write(file,False)

                    with wx.MessageDialog(None, message="Saved file successfully", caption="Save successful", style=wx.ICON_INFORMATION) as dlg:
                        dlg.ShowModal()
                except BaseException:
                    with wx.MessageDialog(None, message="File not saved", caption="Save Failed", style=wx.ICON_ERROR) as dlg:
                        dlg.showModal()
                


class ImportPanel(wx.Panel):
    def __init__(self, parent, authenticated, authCookie, config):
        super().__init__(parent)
        labels = config['Labels']
        self.config = config
        self.authenticated = authenticated
        self.authCookie = authCookie
        self.mappingDict = {}
        self.fileName = ''
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
        self.mappingPicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.mapping_selected)
        mappingRowSizer.Add(self.mappingPicker, 0, wx.ALL, 5)
        self.mappingButton = wx.Button(self, label=labels.get('mainPanelMappingSetupButton','Setup mapping'))
        self.mappingButton.Bind(wx.EVT_BUTTON, self.show_mapping_dialog)
        mappingRowSizer.Add(self.mappingButton, 0, wx.ALL, 5)

        mainSizer.Add(mappingRowSizer)
        mainSizer.AddSpacer(30)

        # file directory and buttons to choose files - exact or begins with

        # collection select

        # button to import

        self.SetSizer(mainSizer)

    def mapping_selected(self, event):
        self.fileName = Path((self.mappingPicker.GetPath()).replace('\\', '/'))
        print(self.fileName)
        _mapping = configparser.ConfigParser()
        _mapping.read(self.fileName)
        print(_mapping.sections())
        for key in _mapping[self.config['Mapping']['mappingSectionName']]:
            row = Mapping(key, _mapping[self.config['Mapping']['mappingSectionName']][key])
            self.mappingDict[row.id] = row


    def show_mapping_dialog(self, event):
        print("open mapping dialog")
        with MappingDialog(self.config, self.mappingDict, self.fileName) as mappingDlg:
            mappingDlg.ShowModal()


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