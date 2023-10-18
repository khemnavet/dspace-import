from PySide6.QtCore import QDir, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog

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

        
