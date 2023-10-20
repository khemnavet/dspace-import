from typing import Optional
from PySide6.QtCore import QDir, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QComboBox

from metadataservice import MetadataService

class FileBrowser(QWidget):
    fileSelected = Signal(str, name="fileSelected")

    def __init__(self, title, file_filter, button_title):
        super().__init__()
        self.file_filter = file_filter
        
        self.file_label = QLabel()
        self.file_label.setText(title)

        self.file_display = QLineEdit()
        #self.file_display.setFixedWidth(180)
        self.file_display.setReadOnly(True)

        self.browse_button = QPushButton(button_title)
        self.browse_button.clicked.connect(self.get_file)

        layout = QHBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_display)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)

    def get_file(self):
        self.file_paths = []

        self.selected_file = QFileDialog.getOpenFileName(self, caption="Choose File", dir=QDir.homePath(), filter=self.file_filter)
        # self.selected_file is a tuple (fileName, selectedFilter)
        # if dialog is cancelled, fileName is '', do not emit signal
        #print(self.selected_file)
        if len(self.selected_file[0]) > 0:
            #print("save selected file")
            self.file_paths.append(self.selected_file[0])
            self.file_display.setText(self.file_paths[0])
            self.fileSelected.emit(self.file_paths[0])

#######################################################################################################################

class SchemaFieldSelect(QWidget):

    def __init__(self, metadata_service: MetadataService) -> None:
        super().__init__()
        self.__metadata_service = metadata_service

        schemas = metadata_service.get_schemas()
        self.schema = QComboBox()
        self.schema.insertItems(0, schemas)
        self.schema.currentIndexChanged.connect(self.schema_changed)

        self.schema_fields = QComboBox()
        self.schema_fields.insertItem(0, "") # blank first field to let user skip
        self.schema_fields.insertItems(1, metadata_service.get_schema_fields(schemas[0]))

        layout = QHBoxLayout()
        layout.addWidget(self.schema)
        layout.addWidget(self.schema_fields)

        self.setLayout(layout)

    def schema_changed(self, index):
        if index > -1:
            schema_fields = self.__metadata_service.get_schema_fields(self.schema.currentText())
            self.schema_fields.clear()
            self.schema_fields.insertItem(0, "")
            self.schema_fields.insertItems(1, schema_fields)