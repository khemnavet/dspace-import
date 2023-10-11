# classes for the pages in the wizard

from gettext import GNUTranslations
from PySide6.QtWidgets import QWizardPage, QLabel, QLineEdit, QGridLayout, QMessageBox
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from config import ImporterConfig
from dataobjects import ImporterData
from dspaceauthservice import AuthException, DspaceAuthService

from communityservice import CommunityException, CommunityService

class DSpaceWizardPages(QWizardPage):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__()
        self._config = config
        self._shared_data = shared_data
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

    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations, shared_data: ImporterData) -> None:
        super().__init__(config=config, lang_i18n=lang_i18n, shared_data=shared_data)
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
                auth_service = DspaceAuthService(self._config, self._shared_data)
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
        super().__init__(config=config, lang_i18n=lang_i18n, shared_data=shared_data)
        self.setTitle(_("collection_page_title"))
        self.setSubTitle(_("collection_page_subtitle"))
        # request to query communities
        self.community_service = CommunityService(config, shared_data)
        try:
            self.community_service.get_top_communities()
        except CommunityException as err:
            self._show_critical_message_box(err)
        
        #combo boxes for communities and collections

