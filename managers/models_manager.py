from PyQt5.QtWidgets import *
import time
class ModelSelection:

    def __init__(self,models, validator_name) -> None:
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Select Model")

        self.layout = QVBoxLayout()
        self.window.setLayout(self.layout)

        self.validator_name = validator_name
        self.models = models
        for name,cls in self.models.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda:self.open_model(cls))
            btn.setMinimumHeight(50)
            self.layout.addWidget(btn)
        
        self.window.setLayout(self.layout)

        self.window.setFixedHeight((len(self.models)*50 + 100))
        self.window.setFixedWidth(200)
        qr = self.window.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.window.move(qr.topLeft())

        self.window.show()
        self.app.exec_()
        self.selected_model = None

    def add_model(self,model):
        self.models.update(model)

    def show_window(self):
        
        return self.selected_model
        
    def open_model(self,cls):
        self.window.close()
        cls(self,self.app,self.validator_name)
        

