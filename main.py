import tomllib
import gettext
import os
from PySide6.QtWidgets import QApplication, QWizard

from config import ImporterConfig
from dataobjects import ImporterData
from metadataservice import MetadataService
from wizardpages import LoginPage, CollectionPage

if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = ImporterConfig(tomllib.load(f))
    #print(config)
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
    
    print(metadata_service.get_schema_fields("dc"))

    # start the application and UI
    app = QApplication([app_name])

    wizard = QWizard()
    wizard.setWindowTitle(_("app_title"))
    # wizard pages
    # login page
    wizard.addPage(LoginPage(config, lang_i18n))
    # collection select page
    wizard.addPage(CollectionPage(config, lang_i18n, shared_data))
    wizard.show()

    app.exec()
