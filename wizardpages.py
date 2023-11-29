# classes for the pages in the wizard

from gettext import GNUTranslations
from PySide6.QtWidgets import QWizard, QWizardPage, QLabel, QLineEdit, QGridLayout, QMessageBox, QComboBox, QPlainTextEdit, QWidget, QScrollArea
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression, Qt, QObject, QThread, Signal

from config import ImporterConfig
from dataobjects import ImporterData, AuthData, YesNo, FileBrowseType, ItemFileMatchType, BundleType, Item, Bundle
from dspaceauthservice import AuthException, DspaceAuthService

from communityservice import CommunityException, CommunityService
from widgets import FileBrowser, SchemaFieldSelect, RadioButton
from excelfileservice import ExcelFileService, ExcelFileException
from fileservice import ItemFileService
from utils import Utils
from itemservice import ItemService, ItemException
from bundleservice import BundleService, BundleException
from bitstreamservice import BitstreamService, BitstreamException

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
    
    def _no_yes_options(self) -> dict:
        return {YesNo.NO: _("No"), YesNo.YES: _("Yes")}
    
    def _file_match_options(self) -> dict:
        return {ItemFileMatchType.EXACT: _("file_name_match_exact"), ItemFileMatchType.BEGINS: _("file_name_match_begins_with")}
    
    def _scroll_area_width(self) -> int:
        #self._config.window_width() - (0.05 * self._config.window_width()) 
        return self._config.window_width() - 25
    
    def _scroll_area_height(self) -> int:
        #self._config.window_height() - (0.25 * self._config.window_height())
        return self._config.window_height() - 125

class LoginPage(DSpaceWizardPages):

    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, auth_data: AuthData) -> None:
        super().__init__(config=config, lang_i18n=lang_i18n)
        self._auth_data = auth_data
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
                auth_service = DspaceAuthService(self._config, self._auth_data)
                auth_service.logon(self.username_edit.text(), self.password_edit.text())
                is_valid = True
            except AuthException:
                self._show_critical_message_box("Invalid username and password")
        else:
            self._show_critical_message_box("The username and password are required")
        return is_valid
        
#######################################################################################################################

class CollectionPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, auth_data: AuthData, shared_data: ImporterData) -> None:
        super().__init__(config=config, lang_i18n=lang_i18n)
        self.shared_data = shared_data

        # to get the communities and collections
        self.community_service = CommunityService(self._config, auth_data)

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
        layout.setRowStretch(3, 1)

        # widget to hold the controls
        container = QWidget()
        container.setLayout(layout)
        container.resize(self._config.window_width(), self._config.window_height())
        # scroll area and add container widget
        scroll = QScrollArea(self)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.resize(self._scroll_area_width(), self._scroll_area_height())
        scroll.update()

        #self.setLayout(layout)

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
        self.shared_data.selected_collection = self.collection_select.currentData()
        return True

#######################################################################################################################

class ExcelFileSelectPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self.shared_data = shared_data

        self.setTitle(_("excel_page_title"))
        self.setSubTitle(_("excel_page_subtitle"))

        # instructions
        instruction_label = QLabel()
        instruction_label.setText(_("excel_page_instructions"))

        # file select for excel file
        self.excel_file = FileBrowser(FileBrowseType.FILE, _("excel_page_import_file_label"), "Excel files (*.xlsx)", _("excel_page_file_select_button"))
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
        layout.setRowStretch(3, 1)

        # widget to hold the controls
        container = QWidget()
        container.setLayout(layout)
        container.resize(self._config.window_width(), self._config.window_height())
        # scroll area and add container widget
        scroll = QScrollArea(self)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.resize(self._scroll_area_width(), self._scroll_area_height())
        scroll.update()
        
        #self.setLayout(layout)
        # register the excel sheet select to make it required
        self.registerField("excelSheet*", self.excel_sheet_select)

    def excel_file_selected(self, file_name):
        #print("in excel file selected handler")
        print(f"importing data from {file_name}")
        # instantiate excel file service
        try:
            self.excelService = ExcelFileService()
            self.excelService.set_file(file_name)
            self.shared_data.item_file = file_name
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
            self.shared_data.item_file_sheet = self.excel_sheet_select.currentText()
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

            self.col_list[col]["schema"] = SchemaFieldSelect(self.shared_data)

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

        # column with the item uuid (optional)
        item_uuid_label = QLabel()
        item_uuid_label.setText(_("mapping_page_item_uuid_column_label"))
        self.item_uuid_select = QComboBox()
        self.item_uuid_select.insertItem(0, "")
        self.item_uuid_select.insertItems(1, column_headings)
        layout.addWidget(item_uuid_label, index, 0)
        layout.addWidget(self.item_uuid_select, index, 1)
        index = index + 1

        # column with primary bitstream file name (optional)
        primary_bitstream_label = QLabel()
        primary_bitstream_label.setText(_("mapping_page_primary_bitstream_label"))
        self.primary_bitstream_select = QComboBox()
        self.primary_bitstream_select.insertItem(0, "")
        self.primary_bitstream_select.insertItems(1, column_headings)
        layout.addWidget(primary_bitstream_label, index, 0)
        layout.addWidget(self.primary_bitstream_select, index, 1)
        index = index + 1

        # if to update existing
        update_existing_label = QLabel()
        update_existing_label.setText(_("mapping_page_update_existing_label"))
        self.update_existing = RadioButton(self._no_yes_options())
        layout.addWidget(update_existing_label, index, 0)
        layout.addWidget(self.update_existing, index, 1)

        # widget to hold the controls
        container = QWidget()
        container.setLayout(layout)
        container.resize(self._config.window_width(), self._config.window_height())
        # scroll area and add container widget
        scroll = QScrollArea(self)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.resize(self._scroll_area_width(), self._scroll_area_height())
        scroll.update()

        # register title_label to make it required
        self.registerField("titleField*", self.title_select)
    
    def validatePage(self) -> bool:
        # validate page, at least one column is mapped to a metadata field
        self.mapping = {}
        for row in self.col_list:
            #print(self.col_list[row]["schema"].selected_schema_field())
            if len(self.col_list[row]["schema"].selected_schema_field()) > 0:
                if not self.col_list[row]["schema"].selected_schema_field() in self.mapping:
                    self.mapping[self.col_list[row]["schema"].selected_schema_field()] = []
                self.mapping[self.col_list[row]["schema"].selected_schema_field()].append(row) # mapping[metadata_field] = list of columns
        if len(self.mapping) == 0:
            self._show_critical_message_box(_("mapping_page_column_schema_mapping_required"))
            return False
        # title is required
        if self.title_select.currentIndex() == 0:
            self._show_critical_message_box(_("mapping_page_title_column_required"))
            return False
        # if update existing is YES, item uuid column has to be chosen
        if self.update_existing.selected_option()[0] == YesNo.YES:
            if self.item_uuid_select.currentIndex() == 0:
                self._show_critical_message_box(_("mapping_page_item_uuid_column_required"))
                return False
        # save selections
        print(f"selected collection = {self.shared_data.selected_collection.name}")
        self.shared_data.column_mapping = self.mapping
        self.shared_data.title_column = self.title_select.currentText()
        self.shared_data.item_uuid_column = self.item_uuid_select.currentText()
        self.shared_data.update_existing = self.update_existing.selected_option()[0]
        self.shared_data.primary_bitstream_column = self.primary_bitstream_select.currentText()
        
        return super().validatePage()
    
#######################################################################################################################

class FilePage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self.shared_data = shared_data

        self.setTitle(_("file_page_title"))
        self.setSubTitle(_("file_page_subtitle"))
    
    def initializePage(self) -> None:
        excelFileService = ExcelFileService()

        # instruction label
        instruction_label = QLabel()
        instruction_label.setText(_("file_page_instructions"))
        instruction_label.setWordWrap(True)

        # directory
        self.file_dir = FileBrowser(FileBrowseType.DIR, _("file_page_item_dir_label"), "", _("file_page_item_dir_select_button"))
        self.file_dir.fileSelected.connect(self.dir_selected)

        # file name columns
        file_name_column_label = QLabel()
        file_name_column_label.setText(_("file_page_file_name_column_label"))
        self.file_name_column = QComboBox()
        self.file_name_column.insertItems(0, excelFileService.get_column_headings())

        # match file name
        match_file_name_label = QLabel()
        match_file_name_label.setText(_("file_page_match_file_name_label"))
        self.match_file_name = RadioButton(self._file_match_options())

        # extension for files
        file_name_extension_label = QLabel()
        file_name_extension_label.setText(_("file_page_file_name_extension_label"))
        self.file_name_extension = QLineEdit()

        # remove existing files for duplicate
        remove_existing_files_label = QLabel()
        remove_existing_files_label.setText(_("file_page_remove_existing_for_duplicate"))
        self.remove_existing_files = RadioButton(self._no_yes_options())

        layout = QGridLayout()
        layout.addWidget(instruction_label, 0, 0, 1, 2)
        layout.addWidget(self.file_dir, 1, 0, 1, 2)
        layout.addWidget(file_name_column_label, 2, 0)
        layout.addWidget(self.file_name_column, 2, 1)
        layout.addWidget(match_file_name_label, 3, 0)
        layout.addWidget(self.match_file_name, 3, 1)
        layout.addWidget(file_name_extension_label, 4, 0)
        layout.addWidget(self.file_name_extension, 4, 1)
        layout.addWidget(remove_existing_files_label, 5, 0)
        layout.addWidget(self.remove_existing_files, 5, 1)
        layout.setRowStretch(6, 1)

        # container for the controls
        container = QWidget()
        container.setLayout(layout)
        container.resize(self._config.window_width(), self._config.window_height())
        # scroll area and add container widget
        scroll = QScrollArea(self)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.resize(self._scroll_area_width(), self._scroll_area_height())
        scroll.update()

        #self.setLayout(layout)

        # any required fields to register?
    
    def dir_selected(self, path):
        self.shared_data.item_directory = path

    def validatePage(self) -> bool:
        # if match_file_name is begins with, file name extension is required
        if self.match_file_name.selected_option()[0] == ItemFileMatchType.BEGINS and len(self.file_name_extension.text().strip()) == 0:
            self._show_critical_message_box(f"The field {_('file_page_file_name_extension_label')} is required")
            return False
        # save values
        self.shared_data.file_name_column = self.file_name_column.currentText()
        self.shared_data.file_name_matching = self.match_file_name.selected_option()[0]
        self.shared_data.file_extension = self.file_name_extension.text().strip()
        self.shared_data.remove_existing_files = self.remove_existing_files.selected_option()[0]
        return True

#######################################################################################################################

class SummaryPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, auth_data: AuthData, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self.shared_data = shared_data
        self.excel_service = ExcelFileService()
        self.item_file_service = ItemFileService()
        self.item_service = ItemService(config, auth_data)

        self.show_summary = False

        self.setTitle(_("summary_page_title"))
        # change name of next button to import
        self.setButtonText(QWizard.NextButton, "Import")

        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)

        layout = QGridLayout()
        layout.addWidget(self.summary)

        self.setLayout(layout)

        self.setCommitPage(True)
    
    def initializePage(self) -> None:
        # check the item files to ensure all exists
        summary_data = []
        for row_index, file_name, item_uuid, item_title in self.excel_service.file_itemuuiud_title(self.shared_data.file_name_column, self.shared_data.item_uuid_column, self.shared_data.title_column):
            #print(f"checking file {file_name} for title {item_title}")
            if file_name is not None and len(self.shared_data.item_directory) > 0 and not self.item_file_service.item_file_exists(file_name, self.shared_data.file_name_matching, self.shared_data.file_extension, self.shared_data.item_directory):
                summary_data.append(f"File not found for row {row_index}, (title {item_title})")
            try:
                if item_uuid is not None and not Utils.valid_uuid(item_uuid):
                    summary_data.append(f"Item UUID for row {row_index} (title {item_title}) is not a valid format")
                elif item_uuid is not None and self.item_service.owning_collection(item_uuid) != self.shared_data.selected_collection.uuid:
                    summary_data.append(f"Item UUID for row {row_index} (title {item_title}) is not in collection {self.shared_data.selected_collection.name}")
            except ItemException as err:
                summary_data.append(f"Item UUID for row {row_index} (title {item_title}) error getting owning collection {err}")

        if len(summary_data) == 0:
            # can import, show summary values
            self.show_summary = True
            summary_data.append(_("summary_page_import_into_collection")+" "+self.shared_data.selected_collection.name)
            summary_data.append(_("summary_page_using_file")+" "+self.shared_data.item_file+", "+_("summary_page_file_sheet")+" "+self.shared_data.item_file_sheet)
            summary_data.append(_("summary_page_title_column")+" "+self.shared_data.title_column)
            summary_data.append(_("summary_page_item_uuid_column")+" "+self.shared_data.item_uuid_column)
            summary_data.append(_("summary_page_update_existing")+" "+(_("Yes") if self.shared_data.update_existing else _("No")))
            summary_data.append(_("summary_page_item_directory")+" "+self.shared_data.item_directory)
        
        self.summary.setPlainText("\n".join(summary_data))

    def isComplete(self) -> bool:
        return self.show_summary
        
#######################################################################################################################

class ImportResultsPage(DSpaceWizardPages):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, auth_data: AuthData, shared_data: ImporterData) -> None:
        super().__init__(config, lang_i18n)
        self.shared_data = shared_data
        self.auth_data = auth_data

        self.processing_completed = False

        self.setTitle(_("import_results_page_title"))

        self.results = QPlainTextEdit()

        layout = QGridLayout()
        layout.addWidget(self.results)

        self.setLayout(layout)
    
    def initializePage(self) -> None:
        self.worker_thread = QThread()
        self.worker = Worker(self.shared_data, self._config, self.auth_data)
        self.worker.moveToThread(self.worker_thread)

        # connect signals and slots
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker.progress.connect(self.report_progress)

        self.worker_thread.finished.connect(self.set_completed)
        self.worker.finished.connect(self.set_completed)
        self.worker_thread.start()
        
    def report_progress(self, str):
        self.results.appendPlainText(str + "\n")

    def set_completed(self):
        self.processing_completed = True
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        return self.processing_completed
    

class Worker(QObject):
    finished = Signal(str, name="finished")
    progress = Signal(str, name="progress")

    def __init__(self, shared_data: ImporterData, config: ImporterConfig, auth_data: AuthData) -> None:

        self.shared_data = shared_data
        self.excel_service = ExcelFileService()
        self.item_service = ItemService(config,auth_data)
        self.bundle_service = BundleService(config, auth_data)
        self.bitstream_service = BitstreamService(config, auth_data)
        self.file_service = ItemFileService()
        super().__init__()

    
    def __remove_bundle_bitstreams(self, bundle):
        if bundle is not None:
            if self.bundle_service.bundle_has_primary_bitstream(bundle):
                self.bundle_service.remove_primary_bitstream(bundle)
            bitstreams = self.bundle_service.bundle_bitstreams(bundle)
            for bitstream in bitstreams:
                self.bitstream_service.remove_bitstream(bitstream)

    def run(self):
        for row_index, file_name, item_uuid, item_title in self.excel_service.file_itemuuiud_title(self.shared_data.file_name_column, self.shared_data.item_uuid_column, self.shared_data.title_column):
            print(f"processing row {row_index}")
            item_updated = False
            try:
                if item_uuid is not None and self.shared_data.update_existing:
                    item = self.item_service.get_item(item_uuid)
                    if self.shared_data.remove_existing_files:
                        original, thumbnail = self.item_service.bundle(item, [BundleType.ORIGINAL, BundleType.THUMBNAIL])
                        self.__remove_bundle_bitstreams(original)
                        self.__remove_bundle_bitstreams(thumbnail)
                    else:
                        original = self.item_service.bundle(item, [BundleType.ORIGINAL])
                    
                    item.metadata = self.excel_service.item_metadata(row_index, self.shared_data.column_mapping)
                    item.name = item_title
                    self.item_service.update_item(item)
                    item_updated = True
                elif item_uuid is None: # do nothing if item_uuid is set and update_existing is No
                    item = self.item_service.create_item(Item(name=item_title, metadata=self.excel_service.item_metadata(row_index, self.shared_data.column_mapping)), self.shared_data.selected_collection)
                    original = self.bundle_service.create_bundle(Bundle(bundle_type=BundleType.ORIGINAL), item)
                    item_updated = True
                
                if len(self.shared_data.primary_bitstream_column) > 0:
                    primary_file = self.excel_service.primary_bitstream_value(row_index, self.shared_data.primary_bitstream_column)
                else:
                    primary_file = None

                if item_updated and file_name is not None and len(self.shared_data.item_directory) > 0:
                    # bitstreams
                    for file in self.file_service.item_files(file_name, self.shared_data.file_name_matching, self.shared_data.file_extension, self.shared_data.item_directory):
                        bitstream = self.bitstream_service.create_bitstream(original, file)
                        if primary_file is not None and file.name == primary_file+self.shared_data.file_extension:
                            self.bundle_service.bundle_add_primary_bitstream(original, bitstream)
                self.progress.emit(f"Imported row {row_index} (title {item_title}) successfully.")

            except ItemException as err:
                self.progress.emit(f"Error processing row {row_index} (title {item_title}). {err}")
            except BundleException as err1:
                self.progress.emit(f"Error processing bundles for row {row_index} (title {item_title}). {err1}")
            except BitstreamException as err2:
                self.progress.emit(f"Error processing bitstreams for row {row_index} (title {item_title}). {err2}")
        
        print("finished")
        self.finished.emit("Finished import")