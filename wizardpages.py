# classes for the pages in the wizard

from abc import ABC
from gettext import GNUTranslations
from PySide6.QtWidgets import QWizardPage, QLabel, QLineEdit, QGridLayout

from config import ImporterConfig


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
        username_edit = QLineEdit()

        password_label = QLabel(text=_("login_page_password_label"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)

        layout = QGridLayout()
        layout.addWidget(username_label, 0, 0)
        layout.addWidget(username_edit, 0, 1)
        layout.addWidget(password_label, 1, 0)
        layout.addWidget(password_edit, 1, 1)

        self.setLayout(layout)
    