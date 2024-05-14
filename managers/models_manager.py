from PyQt5.QtWidgets import *
import time
class ModelSelection:

    def __init__(self) -> None:
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("Select Model")

        self.layout = QVBoxLayout()
        self.window.setLayout(self.layout)

        self.models = dict()
        self.selected_model = None

    def add_model(self,model):
        self.models.update(model)

    def show_window(self):
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
        return self.selected_model
        
    def open_model(self,cls):
        
        self.app.closeAllWindows()
        self.selected_model = cls
        

