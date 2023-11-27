from PySide6.QtCore import QDir, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QComboBox, QRadioButton

from dataobjects import FileBrowseType, ImporterData

class FileBrowser(QWidget):
    fileSelected = Signal(str, name="fileSelected")

    def __init__(self, browse_type: FileBrowseType, title, file_filter, button_title):
        super().__init__()
        self.file_filter = file_filter
        self.browse_type = browse_type
        
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
        if self.browse_type == FileBrowseType.FILE:
            sel_file = QFileDialog.getOpenFileName(self, caption="Choose File", dir=QDir.homePath(), filter=self.file_filter)
            self.selected_file = sel_file[0]
            # self.selected_file is a tuple (fileName, selectedFilter)
            # if dialog is cancelled, fileName is '', do not emit signal
        
        if self.browse_type == FileBrowseType.DIR:
            self.selected_file = QFileDialog.getExistingDirectory(self, caption="Choose Directory", dir=QDir.homePath())
        #print(self.selected_file)
        if len(self.selected_file) > 0:
            #print("save selected file")
            self.file_display.setText(self.selected_file)
            self.fileSelected.emit(self.selected_file)

#######################################################################################################################

class SchemaFieldSelect(QWidget):

    def __init__(self, import_data: ImporterData) -> None:
        super().__init__()
        self.__import_data = import_data

        schemas = import_data.get_schemas()
        self.schema = QComboBox()
        self.schema.insertItems(0, schemas)
        self.schema.currentIndexChanged.connect(self.schema_changed)

        self.schema_fields = QComboBox()
        self.schema_fields.insertItem(0, "") # blank first field to let user skip
        self.schema_fields.insertItems(1, import_data.get_schema_fields(schemas[0]))

        layout = QHBoxLayout()
        layout.addWidget(self.schema)
        layout.addWidget(self.schema_fields)

        self.setLayout(layout)

    def schema_changed(self, index):
        if index > -1:
            schema_fields = self.__import_data.get_schema_fields(self.schema.currentText())
            self.schema_fields.clear()
            self.schema_fields.insertItem(0, "")
            self.schema_fields.insertItems(1, schema_fields)
    
    def selected_schema_field(self):
        return self.schema_fields.currentText()
    
#######################################################################################################################

class RadioButton(QWidget):

    def __init__(self, options: dict):
        super().__init__()

        self.options = options

        radio_layout = QHBoxLayout()
        self.radio = []
        index = 0
        for key, value in options.items():
            self.radio.append(QRadioButton(value, self))
            self.radio[index].value = key
            self.radio[index].toggled.connect(self.update)
            radio_layout.addWidget(self.radio[index])
            index = index + 1
        self.radio[0].setChecked(True)

        self.setLayout(radio_layout)
    
    def update(self):
        radio_button = self.sender()

        #if radio_button.isChecked():
        #    print(f"radio button value: {radio_button.value}, text: {radio_button.text()}")

    def selected_option(self) -> tuple:
        for rb in self.radio:
            if rb.isChecked():
                return (rb.value, rb.text())


