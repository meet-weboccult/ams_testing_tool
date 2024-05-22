from PyQt5.QtWidgets import *
from mobile_classification.mvc_view import View
from mobile_detection import MobileDetection
from occupany_classification.main_window import MainWindow
import sys
class ModelSelection:

    def __init__(self,validator_name) -> None:
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("Select Model")

        self.layout = QVBoxLayout()
        self.window.setLayout(self.layout)

        self.validator_name = validator_name
        
        self.add_model("Mobile Detection",MobileDetection)
        self.add_model("Occupancy Classification",MainWindow)
        self.add_model("Mobile Classification",View)
        
        self.window.setLayout(self.layout)

        self.window.setFixedHeight(300)
        self.window.setFixedWidth(200)
        qr = self.window.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.window.move(qr.topLeft())

        self.window.show()
        self.app.exec_()
        self.selected_model = None


    def add_model(self, name, model):
        btn = QPushButton(name)
        btn.clicked.connect(lambda:self.open_model(name,model))
        btn.setMinimumHeight(50)
        self.layout.addWidget(btn)

    def show_window(self):
        
        return self.selected_model
        
    def open_model(self,name,cls):
        self.window.close()
        object = cls(self,self.app,self.validator_name)
        if name == "test" :
            object.show()