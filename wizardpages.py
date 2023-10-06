# classes for the pages in the wizard

from gettext import GNUTranslations
from PySide6.QtWidgets import QWizardPage, QLabel, QLineEdit, QGridLayout, QMessageBox
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from config import ImporterConfig
from metadataservice import MetadataService


class DSpaceWizardPages(QWizardPage):
    def __init__(self, config: ImporterConfig, lang_i18n: GNUTranslations) -> None:
        super().__init__()
        self.__config = config
        self.__lang_i18n = lang_i18n
        lang_i18n.install()

    def translation_value(self, translation_key: str) -> str:
        return self.__lang_i18n.gettext(translation_key)

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


    def __adjust_text_color(self, editor):
        if not editor.hasAcceptableInput():
            editor.setStyleSheet("QLineEdit { color: red; }")
        else:
            print("has acceptable input")
            editor.setStyleSheet("QLineEdit { color: black; }")
    
    def validatePage(self) -> bool:
        # this is called when next or finished is clicked
        # since registerField is used and the fields are required can only check that they are valid to login to dspace
        # validator on username does not validate string if field not in registerField?
        # return the tokens
        # setup a data structure where the tokens from the login are saved and can be refreshed
        if not(len(self.username_edit.text()) > 0 and len(self.password_edit.text()) > 0):
            msgBox = QMessageBox()
            msgBox.setText("The username and password are required")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.exec()
            return False
        return len(self.username_edit.text()) > 0 and len(self.password_edit.text()) > 0
        

    
