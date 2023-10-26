# classes for the pages in the wizard

from gettext import GNUTranslations
from PySide6.QtWidgets import QWizardPage, QLabel, QLineEdit, QGridLayout, QMessageBox, QComboBox, QHBoxLayout
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from config import ImporterConfig
from dataobjects import ImporterData, DSO
from dspaceauthservice import AuthException, DspaceAuthService

from communityservice import CommunityException, CommunityService
from widgets import FileBrowser, SchemaFieldSelect, RadioButton
from excelfileservice import ExcelFileService, ExcelFileException
from metadataservice import MetadataService

class DSpaceWizardPages(QWizardPage):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations) -> None:
        super().__init__()
        self._config = config
        self._lang_i18n = lang_i18n
        lang_i18n.install()

    def translation_value(self, translation_key: str) -> str:
        return self._lang_i18n.gettext(translation_key)
    
    def _show_critical_message_box(self, message: str):
        msgBox = QMessageBox()
        msgBox.setText(message)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec()

class LoginPage(DSpaceWizardPages):

    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations) -> None:
        super().__init__(config=config, lang_i18n=lang_i18n)
        self.setTitle(_("login_page_title"))
        self.setSubTitle(_("login_page_subtitle"))

        username_label = QLabel(text=_("login_page_username_label"))
        self.username_edit = QLineEdit()

        # validator for username - email address
        re = QRegularExpression("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b", QRegularExpression.CaseInsensitiveOption)
        validator = QRegularExpressionValidator(re)
        self.username_edit.setValidator(validator)
        #username_edit.textChanged.connect(self.__adjust_text_color(username_edit))

        password_label = QLabel(text=_("login_page_password_label"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        layout = QGridLayout()
        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username_edit, 0, 1)
        layout.addWidget(password_label, 1, 0)
        layout.addWidget(self.password_edit, 1, 1)

        self.setLayout(layout)

        # register the fields and make them required
        self.registerField("username*", self.username_edit)
        self.registerField("password*", self.password_edit)

    def validatePage(self) -> bool:
        # this is called when next or finished is clicked
        # since registerField is used and the fields are required can only check that they are valid to login to dspace
        # validator on username does not validate string if field not in registerField?
        # return the tokens
        # setup a data structure where the tokens from the login are saved and can be refreshed
        is_valid = False
        if len(self.username_edit.text()) > 0 and len(self.password_edit.text()) > 0:
            try:
                auth_service = DspaceAuthService(self._config)
                auth_service.logon(self.username_edit.text(), self.password_edit.text())
                is_valid = True
            except AuthException:
                self._show_critical_message_box("Invalid username and password")
        else:
            self._show_critical_message_box("The username and password are required")
        return is_valid
        
#######################################################################################################################

class CollectionPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config=config, lang_i18n=lang_i18n)
        self._shared_data = shared_data

        # to get the communities and collections
        self.community_service = CommunityService(self._config)

        self.setTitle(_("collection_page_title"))
        self.setSubTitle(_("collection_page_subtitle"))

        # instructions
        instruction_label = QLabel()
        instruction_label.setText(_("collection_page_instructions"))
        
        #combo boxes for communities and collections
        community_label = QLabel(text=_("collection_page_community_label"))
        self.community_select = QComboBox()
        self.community_select.currentIndexChanged.connect(self.change_community)

        collection_label = QLabel(text=_("collection_page_collection_label"))
        self.collection_select = QComboBox()

        # community_select.clear will clear all items from select
        layout = QGridLayout()
        layout.addWidget(instruction_label, 0, 0, 1, 2)
        layout.addWidget(community_label, 1, 0)
        layout.addWidget(self.community_select, 1, 1)
        layout.addWidget(collection_label, 2, 0)
        layout.addWidget(self.collection_select, 2, 1)

        self.setLayout(layout)

        # register fields to make them required
        self.registerField("collection*", self.collection_select)
    
    def change_community(self, index):
        if index > 0: # 0 index is blank
            curr_dso = self.community_select.itemData(index)
            # get the sub communities
            sub_comm_list = self.community_service.get_subcommunities(curr_dso) # list of DSO
            self.community_select.clear()
            if curr_dso is None:
                self.community_select.insertItem(0, "")
                index = 1
            else:
                self.community_select.insertItem(0, curr_dso.name)
                if curr_dso.parent is None:
                    self.community_select.insertItem(1, "Back", userData=None)
                else:
                    self.community_select.insertItem(1, "Back", userData=self.community_service.get_community_dso(curr_dso.parent))
                index = 2
            for sub_comm in sub_comm_list:
                self.community_select.insertItem(index, sub_comm.name, userData=sub_comm)
                index = index + 1

            # populate the collections
            coll_list = self.community_service.get_collections(curr_dso) # list of DSO
            self.collection_select.clear()
            index = 0
            for coll in coll_list:
                self.collection_select.insertItem(index, coll.name, userData=coll)
                index = index + 1


    def initializePage(self) -> None:
        try:
            if len(self.community_service.communities_and_collections) == 0:
                # request to query communities
                self.community_service.get_top_communities()
            # populate the community drop down
            self.community_select.insertItem(0, "")
            index = 1
            for _, dso in self.community_service.communities_and_collections.items():
                self.community_select.insertItem(index, dso.name, userData=dso)
                index = index + 1

        except CommunityException as err:
            self._show_critical_message_box(str(err))

    def validatePage(self) -> bool:
        if self.collection_select.currentIndex == -1:
            self._show_critical_message_box("The collection to import the data to is required.")
            return False
        self._shared_data.selected_community = self.collection_select.currentData()
        return True

#######################################################################################################################

class ExcelFileSelectPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self._shared_data = shared_data

        self.setTitle(_("excel_page_title"))
        self.setSubTitle(_("excel_page_subtitle"))

        # instructions
        instruction_label = QLabel()
        instruction_label.setText(_("excel_page_instructions"))

        # file select for excel file
        self.excel_file = FileBrowser(_("excel_page_import_file_label"), "Excel files (*.xlsx)", _("excel_page_file_select_button"))
        self.excel_file.fileSelected.connect(self.excel_file_selected)
        # sheet in excel file
        excel_sheet_label = QLabel()
        excel_sheet_label.setText(_("excel_page_sheet_label"))
        self.excel_sheet_select = QComboBox()

        layout = QGridLayout()
        layout.addWidget(instruction_label, 0, 0, 1, 2)
        layout.addWidget(self.excel_file, 1, 0, 1, 2)
        layout.addWidget(excel_sheet_label, 2, 0)
        layout.addWidget(self.excel_sheet_select, 2, 1)

        self.setLayout(layout)
        # register the excel sheet select to make it required
        self.registerField("excelSheet*", self.excel_sheet_select)

    def excel_file_selected(self, file_name):
        #print("in excel file selected handler")
        print(f"importing data from {file_name}")
        # instantiate excel file service
        try:
            self.excelService = ExcelFileService()
            self.excelService.set_file(file_name)
            # extract sheets and populate the excel_sheet_select widget
            self.excel_sheet_select.clear()
            self.excel_sheet_select.insertItems(0, self.excelService.get_sheet_names())
        except ExcelFileException as err:
            self.excel_sheet_select.clear()
            self._show_critical_message_box(str(err))
    
    def validatePage(self) -> bool:
        # selected sheet - get the columns headings of the selected sheet
        try:
            self.excelService.set_column_headings(self.excel_sheet_select.currentText())
        except ExcelFileException as err:
            self._show_critical_message_box(str(err))
            return False
        return super().validatePage()

#######################################################################################################################

class MappingPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self.shared_data = shared_data

        self.setTitle(_("mapping_page_title"))
        self.setSubTitle(_("mapping_page_subtitle"))

    def initializePage(self) -> None:
        excelFileService = ExcelFileService()
        metadataService = MetadataService(self._config)

        # table layout for the mapping
        layout = QGridLayout()
        instruction_label = QLabel()
        instruction_label.setText(_("mapping_page_instructions"))
        layout.addWidget(instruction_label, 0, 0, 1, 2)

        column_label = QLabel()
        column_label.setText(_("mapping_page_column_heading"))
        metadata_label = QLabel()
        metadata_label.setText(_("mapping_page_metadata_heading"))
        layout.addWidget(column_label, 1, 0)
        layout.addWidget(metadata_label, 1, 1)

        # display the columns
        self.col_list = {}
        index = 2
        column_headings = excelFileService.get_column_headings()
        for col in column_headings:
            self.col_list[col] = {}
            self.col_list[col]["col_label"] = QLabel()
            self.col_list[col]["col_label"].setText(col)

            self.col_list[col]["schema"] = SchemaFieldSelect(metadataService)

            layout.addWidget(self.col_list[col]["col_label"], index, 0)
            layout.addWidget(self.col_list[col]["schema"], index, 1)
            index = index + 1
        
        # specify title column, 
        title_label = QLabel()
        title_label.setText(_("mapping_page_title_column_label"))
        self.title_select = QComboBox()
        self.title_select.insertItem(0, "")
        self.title_select.insertItems(1, column_headings)
        layout.addWidget(title_label, index, 0)
        layout.addWidget(self.title_select, index, 1)
        index = index + 1

        # column to check for duplicates
        duplicate_label = QLabel()
        duplicate_label.setText(_("mapping_page_duplicate_column_label"))
        self.duplicate_select = QComboBox()
        self.duplicate_select.insertItem(0, "")
        self.duplicate_select.insertItems(1, column_headings)
        layout.addWidget(duplicate_label, index, 0)
        layout.addWidget(self.duplicate_select, index, 1)
        index = index + 1

        # if to update existing
        update_existing_label = QLabel()
        update_existing_label.setText(_("mapping_page_update_existing_label"))
        self.update_existing = RadioButton({"NO": "No", "YES": "Yes"})
        layout.addWidget(update_existing_label, index, 0)
        layout.addWidget(self.update_existing, index, 1)

        self.setLayout(layout)

        # register title_label to make it required
        self.registerField("titleField*", self.title_select)
    
    def validatePage(self) -> bool:
        # validate page, at least one column is mapped to a metadata field
        cols_mapped = 0
        self.mapping = {}
        for row in self.col_list:
            self.mapping[row] = self.col_list[row]["schema"].selected_schema_field()
            #print(self.col_list[row]["schema"].selected_schema_field())
            if len(self.col_list[row]["schema"].selected_schema_field()) > 0:
                cols_mapped = cols_mapped + 1
        if cols_mapped == 0:
            self._show_critical_message_box(_("mapping_page_column_schema_mapping_required"))
            return False
        # title is required
        if self.title_select.currentIndex == 0:
            self._show_critical_message_box(_("mapping_page_title_column_required"))
            return False
        # save selections
        print(f"selected collection = {self.shared_data.selected_community.name}")
        self.shared_data.column_mapping = self.mapping
        self.shared_data.title_column = self.title_select.currentText()
        self.shared_data.duplicate_column = self.duplicate_select.currentText()
        self.shared_data.update_existing = self.update_existing.selected_option()[0]
        return super().validatePage()