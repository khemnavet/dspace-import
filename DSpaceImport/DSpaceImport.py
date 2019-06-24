# classes for the ui
import wx
import wx.grid as gridlib
import wx.lib.scrolledpanel as scrolled
import configparser
import pandas as pd
from pathlib import Path

from DataObjects import Mapping, DSOTypes, DSO
import dspacerequests

class LogonDialog(wx.Dialog):
    def __init__(self, config, dspaceRequests):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('logonDialogTitle','Login'))
        self.loginCookie = None
        self.loggedIn = False
        self.config = config
        self.dspaceRequest = dspaceRequests

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
        try:
            self.loginCookie = self.dspaceRequest.dspace_logon(self.email.GetValue(), self.password.GetValue())
            self.loggedIn = True
            self.Close()
        except Exception as e:
            with wx.MessageDialog(None, message=str(e), caption=self.config['Messages']['loginMessageBoxTitle'], style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            self.password.SetValue('')


class MappingDialog(wx.Dialog):
    def __init__(self, config, mappingData, fileName):
        labels = config['Labels']
        wx.Dialog.__init__(self, None, title=labels.get('mappingDialogTitle','Mapping'), size=(500,500))
        self.mappingData = mappingData
        self.fileName = fileName
        self.config = config

        print(fileName)

        panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        panel.SetupScrolling()

        self.mappingListCtrl = gridlib.Grid(panel)
        self.mappingListCtrl.CreateGrid(numRows=len(mappingData)+int(config['Mapping']['mappingNumberOfRows']), numCols=2)
        self.mappingListCtrl.SetColLabelValue(0, labels.get('mappingControlFileColumnLabel', 'Column'))
        self.mappingListCtrl.SetColLabelValue(1, labels.get('mappingControlMetadataFieldLabel', 'Field'))
        self.mappingListCtrl.SetColSize(0, -1)
        self.mappingListCtrl.SetColSize(1, -1)

        index = 0
        for key,val in mappingData.items():
            print('{} {}'.format(index, val.colName))
            self.mappingListCtrl.SetCellValue(index, 0, val.colName)
            self.mappingListCtrl.SetCellValue(index, 1, val.metadataField)
            index = index + 1

        self.mappingListCtrl.AutoSizeColumns()
        dialogSizer = wx.BoxSizer(wx.VERTICAL)
        dialogSizer.Add(self.mappingListCtrl, 0, wx.ALL|wx.EXPAND, 5)
        saveButton = wx.Button(panel, label=labels.get('mappingDialogSaveButton','Save'))
        saveButton.Bind(wx.EVT_BUTTON, self.save_mapping)
        dialogSizer.AddSpacer(10)
        dialogSizer.Add(saveButton, 0, wx.ALL, 5)
        dialogSizer.AddSpacer(20)
        panel.SetSizer(dialogSizer)
        # self.Fit()

    def save_mapping(self, event):
        print("save button clicked")
        self.mappingData.clear()
        _newMapping = configparser.ConfigParser()
        _newMapping.add_section(self.config['Mapping']['mappingSectionName'])
        for index in range(0,self.mappingListCtrl.GetNumberRows()):
            if len(self.mappingListCtrl.GetCellValue(index, 0).strip()) > 0 and len(self.mappingListCtrl.GetCellValue(index, 1).strip()) > 0:
                row = Mapping(self.mappingListCtrl.GetCellValue(index, 0).strip().upper(), self.mappingListCtrl.GetCellValue(index, 1).strip())
                self.mappingData[row.colName] = row
                _newMapping.set(self.config['Mapping']['mappingSectionName'], row.colName, row.metadataField)
        # prompt user to save the mapping 
        with wx.FileDialog(self, message=self.config['Messages']['fileSaveAsMessage'], defaultDir=str(self.fileName.parent), defaultFile=self.fileName.name, wildcard=self.config['FileTypeWildcard']['mapFileWildcard'], style=wx.FD_SAVE) as saveDialog:
            if saveDialog.ShowModal() == wx.ID_OK:
                path = Path((saveDialog.GetPath()).replace('\\', '/'))
                # write the file
                try:
                    with open(path, "wt") as file:
                        _newMapping.write(file,False)

                    with wx.MessageDialog(None, message=self.config['Messages']['fileSaveSuccessfulMessage'], caption=self.config['Messages']['fileSaveSuccessfulBoxTitle'], style=wx.ICON_INFORMATION) as dlg:
                        dlg.ShowModal()
                except BaseException:
                    with wx.MessageDialog(None, message=self.config['Messages']['fileSaveFailedMessage'], caption=self.config['Messages']['fileSaveFailedBoxTitle'], style=wx.ICON_ERROR) as dlg:
                        dlg.showModal()
                


class ImportPanel(wx.Panel):
    def __init__(self, parent, authenticated, authCookie, config, dspaceRequests):
        super().__init__(parent)
        labels = config['Labels']

        # class variables
        self.config = config
        self.authenticated = authenticated
        self.authCookie = authCookie
        self.mappingDict = {}
        self.fileName = Path.home()/self.config['Mapping']['mappingFileName']
        self.importFile = None
        self.excelFileObj = None
        self.importDataFrame = None
        self.dspaceRequests = dspaceRequests
        self.topCommunities = []
        self.DSOs = {}

        print(self.fileName)

        # layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(wx.StaticText(self, label=labels.get('mainPanelDescription','')), 0, wx.ALL, 5)

        # select excel file row
        excelRowSizer = wx.BoxSizer(wx.VERTICAL)
        excelRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelFilePickerLabel','Select file')), 0, wx.ALL, 5)
        self.excelPicker = wx.FilePickerCtrl(self, wildcard=self.config['FileTypeWildcard']['excelFileDescription']+'(*'+self.config['FileTypeWildcard']['excelFileType']+')|*'+self.config['FileTypeWildcard']['excelFileType'])
        self.excelPicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.import_file_selected)
        excelRowSizer.Add(self.excelPicker, 0, wx.ALL|wx.EXPAND, 5)
        excelSheetSizer = wx.BoxSizer(wx.HORIZONTAL)
        excelSheetSizer.Add(wx.StaticText(self, label=labels.get('mainPanelFilePickerChooseSheetLabel','Select sheet')), 0, wx.ALL, 5)
        self.excelSheet = wx.Choice(self)
        self.excelSheet.Bind(wx.EVT_CHOICE, self.import_sheet_selected)
        excelSheetSizer.Add(self.excelSheet, 0, wx.ALL, 5)
        excelRowSizer.Add(excelSheetSizer)
        mainSizer.Add(excelRowSizer)
        mainSizer.AddSpacer(2)
        mainSizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.AddSpacer(2)

        # mapping button
        mappingRowSizer = wx.BoxSizer(wx.VERTICAL)
        mappingRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelMappingDescription','Mapping setup')), 0, wx.ALL, 5)
        mappingRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelMappingFilePickerLabel','Select mapping file')), 0, wx.ALL, 5)
        self.mappingPicker = wx.FilePickerCtrl(self, wildcard=self.config['FileTypeWildcard']['mapFileWildcard'])
        #add an event to this and process the file opened
        self.mappingPicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.mapping_selected)
        mappingRowSizer.Add(self.mappingPicker, 0, wx.ALL, 5)
        self.mappingButton = wx.Button(self, label=labels.get('mainPanelMappingSetupButton','Setup mapping'))
        self.mappingButton.Bind(wx.EVT_BUTTON, self.show_mapping_dialog)
        mappingRowSizer.Add(self.mappingButton, 0, wx.ALL, 5)

        dupColRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        dupColRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelMappingDuplicateCheckField','Duplicate Field')), 0, wx.ALL, 5)
        self.duplicateField = wx.Choice(self)
        dupColRowSizer.Add(self.duplicateField, 0, wx.ALL, 5)
        mappingRowSizer.Add(dupColRowSizer, 0, wx.ALL, 5)

        mainSizer.Add(mappingRowSizer)
        mainSizer.AddSpacer(2)
        mainSizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.AddSpacer(2)

        # file directory and buttons to choose files - exact or begins with
        fileDirRowSizer = wx.BoxSizer(wx.VERTICAL)
        fileDirRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemFileUploadDescription','Item Files')), 0, wx.ALL, 5)
        fileDirRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemFileUploadDirPickerLabel','Directory containing files')), 0, wx.ALL, 5)
        self.itemFileDirPicker = wx.DirPickerCtrl(self)
        fileDirRowSizer.Add(self.itemFileDirPicker, 0, wx.ALL, 5)

        uploadColRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        uploadColRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemFileUploadColumnLabel','Item File Column')), 0, wx.ALL, 5)
        self.itemFileField = wx.Choice(self)
        uploadColRowSizer.Add(self.itemFileField, 0, wx.ALL, 5)
        fileDirRowSizer.Add(uploadColRowSizer, 0, wx.ALL, 5)

        itemExtRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        itemExtRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemFileUploadFileExt','Item File Extension')), 0, wx.ALL, 5)
        self.itemFileExtension = wx.TextCtrl(self)
        itemExtRowSizer.Add(self.itemFileExtension, 0, wx.ALL, 5)
        fileDirRowSizer.Add(itemExtRowSizer, 0, wx.ALL, 5)

        self.itemFileProcess = wx.RadioBox(self, label=labels.get('mainPanelItemFileUploadProcessLabel','Item File Matching') , pos=(80,10), choices=[labels.get('mainPanelItemFileUploadProcessOptionExact'), labels.get('mainPanelItemFileUploadProcessOptionBegins')], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        # self.itemFileProcess.GetStringSelection() has the text of the selected control
        fileDirRowSizer.Add(self.itemFileProcess, 0, wx.ALL, 5)

        mainSizer.Add(fileDirRowSizer)
        mainSizer.AddSpacer(2)
        mainSizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.AddSpacer(2)

        # collection select
        collectionSelectRowSizer = wx.BoxSizer(wx.VERTICAL)
        collectionSelectRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemCollectionDescription','Select Collection')), 0, wx.ALL, 5)

        communityRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        communityRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemCommunityLabel', 'Community')), 0, wx.ALL, 5)
        #self.community = wx.ComboBox(self)
        self.community = wx.Choice(self, style=wx.VSCROLL)
        # event handler
        #self.community.Bind(wx.EVT_COMBOBOX, self.community_selected)
        self.community.Bind(wx.EVT_CHOICE, self.community_selected)
        communityRowSizer.Add(self.community, 0, wx.ALL, 5)
        collectionSelectRowSizer.Add(communityRowSizer)

        collectionRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        collectionRowSizer.Add(wx.StaticText(self, label=labels.get('mainPanelItemCollectionLabel', 'Collection')), 0, wx.ALL, 5)
        self.collection = wx.Choice(self)
        collectionRowSizer.Add(self.collection, 0, wx.ALL, 5)
        collectionSelectRowSizer.Add(collectionRowSizer)

        # populate with top collections
        self.get_top_communities()

        mainSizer.Add(collectionSelectRowSizer)

        mainSizer.AddSpacer(2)
        mainSizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.AddSpacer(2)

        # button to import
        self.importButton = wx.Button(self, label=labels.get('mainPanelImportButtonLabel','Import'))
        self.importButton.Bind(wx.EVT_BUTTON, self.do_import)
        mainSizer.Add(self.importButton, 0, wx.ALL, 5)

        self.SetSizer(mainSizer)


    def mapping_selected(self, event):
        self.fileName = Path((self.mappingPicker.GetPath()).replace('\\', '/'))
        print(self.fileName)
        _mapping = configparser.ConfigParser()
        _mapping.read(self.fileName)
        print(_mapping.sections())
        self.mappingDict.clear()
        for key in _mapping[self.config['Mapping']['mappingSectionName']]:
            row = Mapping(key.upper(), _mapping[self.config['Mapping']['mappingSectionName']][key])
            self.mappingDict[row.colName] = row
        # add columns for those in excel file but not in the mapping file
        for col in self.importDataFrame.columns:
            if col.upper() not in self.mappingDict:
                row = Mapping(col.upper(), '')
                self.mappingDict[row.colName] = row
        self.set_column_choices()

    def import_file_selected(self, event):
        try:
            self.importFile = Path((self.excelPicker.GetPath()).replace('\\','/'))
            print(self.importFile)
            print(self.importFile.suffix)
            self.excelFileObj = pd.ExcelFile(self.importFile)
            self.excelSheet.SetItems(self.excelFileObj.sheet_names)
            self.excelSheet.InvalidateBestSize() 
            self.excelSheet.SetSize(self.excelSheet.GetBestSize()) 
            
        except Exception as e:
            with wx.MessageDialog(None, message=str(e), caption=self.config['Messages']['importFileErrorBoxTitle'], style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()
            self.importFile.SetPath('')
            self.excelSheet.Clear()
            self.importFile = None
            self.excelFileObj = None
        finally:
            self.mappingPicker.SetPath('')
            self.fileName = Path.home()/self.config['Mapping']['mappingFileName']
            self.importDataFrame = None
            self.duplicateField.Clear()
            self.itemFileField.Clear()
            self.Layout()

    def import_sheet_selected(self, event):
        try:
            print(self.excelSheet.GetSelection())
            self.importDataFrame = self.excelFileObj.parse(self.excelSheet.GetSelection())
            self.importDataFrame.columns = map(str.upper, self.importDataFrame.columns) # convert the column names to upper case
            self.mappingDict.clear()
            for col in self.importDataFrame.columns:
                row = Mapping(col, '')
                self.mappingDict[col] = row
            self.set_column_choices()
        except Exception as e:
            with wx.MessageDialog(None, message=str(e), caption=self.config['Messages']['importFileErrorBoxTitle'], style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()

    def show_mapping_dialog(self, event):
        print("open mapping dialog")
        with MappingDialog(self.config, self.mappingDict, self.fileName) as mappingDlg:
            mappingDlg.ShowModal()
            self.mappingDict = mappingDlg.mappingData
            self.set_column_choices()

    def set_column_choices(self):
        _choices = ['']
        for key,val in self.mappingDict.items():
            _choices.append(val.colName)

        self.duplicateField.Clear()
        self.duplicateField.SetItems(_choices)
        # self.duplicateField.SetSelection(0)

        self.itemFileField.Clear()
        self.itemFileField.SetItems(_choices)
        # self.itemFileField.SetSelection(0)

    def get_top_communities(self):
        try:
            self.DSOs.clear()
            _top = self.dspaceRequests.dspace_top_communities()
            for _comm in _top:
                dso = DSO(_comm['uuid'], _comm['name'], None, DSOTypes.COMMUNITY)
                self.DSOs[dso.id] = dso
                # add the sub communities
                for _subcom in _comm['subcommunities']:
                    sdso = DSO(_subcom['uuid'], _subcom['name'], dso.id, DSOTypes.COMMUNITY)
                    dso.addChild(sdso.id)
                    self.DSOs[sdso.id] = sdso
                # add the collections
                for _coll in _comm['collections']:
                    sdso = DSO(_coll['uuid'], _coll['name'], dso.id, DSOTypes.COLLECTION)
                    self.DSOs[sdso.id] = sdso
                    dso.addCollection(sdso.id)
                self.DSOs[dso.id].itemsLoaded = True
                self.topCommunities.append(dso.id)
        except Exception as e:
            print(str(e))
        finally:
            self._populate_community()
            self.collection.Clear()

    def _populate_community(self, parent = None, currCommunity = None):
        self.community.Clear() # remove existing items in combobox
        if (parent is None and currCommunity is None):
            # show the top communities
            for tc in self.topCommunities:
                self.community.Append(self.DSOs[tc].name, self.DSOs[tc])
        else:
            self.community.Append(self.DSOs[currCommunity].name, self.DSOs[currCommunity])
            if (parent is None):
                self.community.Append(self.config['Labels']['mainPanelItemCollectionBackLabel'], None)
            else:
                self.community.Append(self.config['Labels']['mainPanelItemCollectionBackLabel'], self.DSOs[parent])
            # children of currCommunity
            for child in self.DSOs[currCommunity].children:
                self.community.Append(self.DSOs[child].name, self.DSOs[child])
            self.community.SetSelection(0)

    def _populate_collection(self, currCommunity):
        self.collection.Clear()
        for coll in self.DSOs[currCommunity].collections:
            self.collection.Append(self.DSOs[coll].name, self.DSOs[coll])
        self.collection.InvalidateBestSize() 
        self.collection.SetSize(self.collection.GetBestSize()) 
        self.Layout() 

    def community_selected(self, event):
        obj = self.community.GetClientData(self.community.GetSelection())
        if (obj is None):
            # going back to the top communities
            self._populate_community()
            self.collection.Clear()
        else:
            print("{}, {}".format(obj.uuid, obj.name))
            # check if children/collections are loaded
            if not obj.itemsLoaded:
                try:
                    _comms = self.dspaceRequests.dspace_community(obj.uuid)
                    for _comm in _comms['subcommunities']:
                        print('adding community {} to dict'.format(_comm['name']))
                        dso = DSO(_comm['uuid'], _comm['name'], obj.id, DSOTypes.COMMUNITY)
                        self.DSOs[dso.id] = dso
                        self.DSOs[obj.id].addChild(dso.id)
                    for _coll in _comms['collections']:
                        print('adding collection {} to dict'.format(_coll['name']))
                        dso = DSO(_coll['uuid'], _coll['name'], obj.id, DSOTypes.COLLECTION)
                        self.DSOs[dso.id] = dso
                        self.DSOs[obj.id].addCollection(dso.id)
                    self.DSOs[obj.id].itemsLoaded = True
                except Exception as e:
                    print(str(e))
            # get the children and add to list
            self._populate_community(obj.parent, obj.id)
            self._populate_collection(obj.id)

    def _form_encoded_row(self, row):
        _data = {}
        #for key,val in self.mappingDict.items():
        #    if len(val.metadataField) > 0:
        #        _data[val.metadataField] = row[val.colName]
        for key in (key for key in self.mappingDict if len(self.mappingDict[key].metadataField) > 0):
            print('metadata = {}, column = {}, value = {}'.format(self.mappingDict[key].metadataField, self.mappingDict[key].colName, row[self.mappingDict[key].colName]))
            _data[self.mappingDict[key].metadataField] = row[self.mappingDict[key].colName]
        return _data

    def do_import(self, event):
        try:
            # excel file loaded
            if self.excelFileObj is None:
                raise Exception(self.config['Messages']['importButtonExcelFileNotLoadedError'])
            # mapping setup or loaded
            if len(self.mappingDict) == 0:
                raise Exception(self.config['Messages']['importButtonMappingNotSetError'])
            # at least one column should be mapped to a metadata field
            if len(list(key for key in self.mappingDict if len(self.mappingDict[key].metadataField) > 0)) == 0:
                raise Exception(self.config['Messages']['importButtonMappingAtLeastOneMetadata'])
            # collection selected
            if self.collection.GetSelection() == wx.NOT_FOUND:
                raise Exception(self.config['Messages']['importButtonCollectionNotSelectedError'])
            # if dir containing files entered, the file column has to be selected
            if len(self.itemFileDirPicker.GetPath()) > 0: 
                if self.itemFileField.GetSelection() == wx.NOT_FOUND:
                    raise Exception(self.config['Messages']['importButtonFileNameFieldError'])
                if self.itemFileProcess.GetSelection() == wx.NOT_FOUND:
                    raise Exception(self.config['Messages']['importButtonFileProcessRadioNotChosen'])

                _ext = ''
                if len(self.itemFileExtension.GetValue().strip()) > 0:
                    _ext = self.itemFileExtension.GetValue().strip()
                    _ext = _ext if _ext.startswith('.') else '.'+_ext
                print('extension is {}'.format(_ext))

                print('item file process {}'.format(self.itemFileProcess.GetSelection()))
                # if dir containing files entered, check if any rows in the excel file has missing file names. 
                _fileDir = Path((self.itemFileDirPicker.GetPath()).replace('\\','/'))
                _numMissing = 0
                _missingList = []
                if self.itemFileProcess.GetSelection() == 0: # exact matching
                    for fname in self.importDataFrame[self.itemFileField.GetString(self.itemFileField.GetSelection())]:
                        # if filename set - can have records without filenames
                        if len(fname.strip()) > 0:
                            _file = _fileDir/(fname.strip()+_ext)
                            # print('checking file {} exists'.format(_file))
                            if not _file.exists():
                                _numMissing = _numMissing + 1
                                _missingList.append(fname)
                elif self.itemFileProcess.GetSelection() == 1: # begins with matching
                    for fname in self.importDataFrame[self.itemFileField.GetString(self.itemFileField.GetSelection())]:
                        # if filename set - can have records without filenames
                        if len(fname.strip()) > 0:
                            print('looking for files that match {}'.format(fname+'*'+_ext))
                            _file = list(_fileDir.glob(fname+'*'+_ext)) # returns a list
                            if len(_file) == 0:
                                _numMissing - _numMissing + 1
                                _missingList.append(fname)

                if _numMissing > 0:
                    raise Exception(self.config['Messages']['importButtonFileMissing']+'\n'+'\n'.join(map(str, _missingList)))

            # items can be imported
            # loop over dataframe and generate dict to send to server
            print('importing data')
            for index, row in self.importDataFrame.iterrows():
                # mapping between row and dc fields
                print('data for for {}'.format(index))
                # print(row)
                _data = self._form_encoded_row(row)
                print(_data)

        except Exception as e:
            with wx.MessageDialog(None, message=str(e), caption=self.config['Messages']['importButtonErrorBoxTitle'], style=wx.ICON_ERROR) as dlg:
                dlg.ShowModal()


class ImportFrame(wx.Frame):
    def __init__(self, config, dspaceRequests):
        labels = config['Labels']
        super().__init__(None, title=labels.get('appMainTitle','Import'), size=(400,800))

        with LogonDialog(config, dspaceRequests) as logonDlg:
            logonDlg.ShowModal()
            self.authenticated = logonDlg.loggedIn
            self.authCookie = logonDlg.loginCookie
        
        if not self.authenticated:
            self.Close()
        else :
            print (self.authenticated)
            panel = ImportPanel(self, self.authenticated, self.authCookie, config, dspaceRequests)
            self.Show()


if __name__ == '__main__':
    # load config
    config = configparser.ConfigParser(empty_lines_in_values=False)
    config.read('config.ini')
    print(config.sections())
    dspaceRequest = dspacerequests.DspaceRequests(config)
    app = wx.App(False)
    frame = ImportFrame(config, dspaceRequest)
    app.MainLoop()