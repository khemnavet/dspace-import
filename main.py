import tomllib
import gettext
import os
from sys import platform
from PySide6.QtWidgets import QApplication, QWizard

from config import ImporterConfig, ConfigException
from dataobjects import ImporterData
from metadataservice import MetadataService
from wizardpages import LoginPage, CollectionPage, ExcelFileSelectPage, MappingPage, FilePage, SummaryPage, ImportResultsPage

if __name__ == "__main__":
    try:
        with open("config.toml", "rb") as f:
            config = ImporterConfig(tomllib.load(f))
    except ConfigException as err:
        print(str(err))
        exit(0)
    
    print(config.dspace_rest_url())

    app_name = "dspace_importer"
    locale_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')

    lang_i18n = gettext.translation(app_name, locale_dir, fallback=False, languages=[config.locale()])
    lang_i18n.install()
    #_ = lang_i18n.gettext

    # get the metadata schemas and fields for each
    metadata_service = MetadataService(config)
    metadata_service.populate_metadata_schemas()

    # shared data
    shared_data = ImporterData()

    # start the application and UI
    app = QApplication([app_name])

    wizard = QWizard()
    wizard.setWindowTitle(_("app_title"))
    if platform == "darwin":
        wizard.setWizardStyle(QWizard.MacStyle)
    else:
        wizard.setWizardStyle(QWizard.ModernStyle)
    
    wizard.resize(config.window_width(), config.window_height())
    # wizard pages
    # login page
    wizard.addPage(LoginPage(config, lang_i18n))
    # collection select page
    wizard.addPage(CollectionPage(config, lang_i18n, shared_data))
    # excel file chooser page
    wizard.addPage(ExcelFileSelectPage(config, lang_i18n, shared_data))
    # mapping page
    wizard.addPage(MappingPage(config, lang_i18n, shared_data))
    # file page
    wizard.addPage(FilePage(config, lang_i18n, shared_data))
    # summary page
    wizard.addPage(SummaryPage(config, lang_i18n, shared_data))
    #results page
    wizard.addPage(ImportResultsPage(config, lang_i18n, shared_data))
    wizard.show()

    app.exec()
