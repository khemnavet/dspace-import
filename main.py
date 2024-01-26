import tomllib
import gettext
import os
import sys
from PySide6.QtWidgets import QApplication, QWizard

from config import ImporterConfig, ConfigException
from dataobjects import ImporterData, AuthData
from metadataservice import MetadataService
from wizardpages import LoginPage, CollectionPage, ExcelFileSelectPage, MappingPage, FilePage, SummaryPage, ImportResultsPage

# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def resource(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    try:
        with open(resource("config.toml"), "rb") as f:
            config = ImporterConfig(tomllib.load(f))
    except ConfigException as err:
        print(str(err))
        exit(0)
    
    print(config.dspace_rest_url())

    app_name = "dspace_importer"
    #locale_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    locale_dir = resource('locale')
    print(locale_dir)
    print(config.locale())

    lang_i18n = gettext.translation(app_name, locale_dir, fallback=False, languages=[config.locale()])
    lang_i18n.install()
    #_ = lang_i18n.gettext

    # shared data
    shared_data = ImporterData()
    auth_data = AuthData()

    # get the metadata schemas and fields for each
    metadata_service = MetadataService(config, auth_data)
    shared_data.set_metadata_schemas(metadata_service.populate_metadata_schemas())

    # start the application and UI
    app = QApplication([app_name])

    wizard = QWizard()
    wizard.setWindowTitle(_("app_title"))
    if sys.platform == "darwin":
        wizard.setWizardStyle(QWizard.MacStyle)
    else:
        wizard.setWizardStyle(QWizard.ModernStyle)
    
    wizard.resize(config.window_width(), config.window_height())
    # wizard pages
    # login page
    wizard.addPage(LoginPage(config, lang_i18n, auth_data))
    # collection select page
    wizard.addPage(CollectionPage(config, lang_i18n, auth_data, shared_data))
    # excel file chooser page
    wizard.addPage(ExcelFileSelectPage(config, lang_i18n, shared_data))
    # mapping page
    wizard.addPage(MappingPage(config, lang_i18n, shared_data))
    # file page
    wizard.addPage(FilePage(config, lang_i18n, shared_data))
    # summary page
    wizard.addPage(SummaryPage(config, lang_i18n, auth_data, shared_data))
    #results page
    wizard.addPage(ImportResultsPage(config, lang_i18n, auth_data, shared_data))
    wizard.show()

    app.exec()
