from PyQt5.QtWidgets import *

class NameDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Your Name")
        layout = QVBoxLayout()
        self.name_label = QLabel("Enter your name:")
        self.name_edit = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.accept)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.exit_button)
        self.resize(400,200)
        self.setLayout(layout)

    def get_name(self):
        return self.name_edit.text()