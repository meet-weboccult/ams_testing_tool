from PyQt5.QtWidgets import  *
from PyQt5.QtCore import Qt


class AuthenticationGUI:
           
    def create_layout(self, submit_handler) -> None:
        self.app = QApplication([])
        self.create_window()
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        
        validator_lbl = QLabel("Enter Validator name :")

        validator_txtbox = QLineEdit()
        validator_txtbox.textChanged.connect(self.on_text_change)
        
        self.submit_btn = QPushButton("Login")
        self.submit_btn.setDisabled(True)
        self.submit_btn.clicked.connect(lambda : submit_handler(validator_name = validator_txtbox.text()))

        self.layout.addWidget(validator_lbl)
        self.layout.addWidget(validator_txtbox)
        self.layout.addWidget(self.submit_btn)

        self.window.setLayout(self.layout)

        self.window.show()
        self.app.exec_()

    def on_text_change(self,text):
        if text == "":
            self.submit_btn.setDisabled(True)
        else:
            self.submit_btn.setDisabled(False)
        
    def create_window(self):
        self.window = QWidget() 
        self.window.setFixedSize(300,200)
        self.window.setWindowTitle("Authentication")
        
        qr = self.window.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.window.move(qr.topLeft())
        
class AuthenticationManager:

    def start_authentication(self):
        self.gui = AuthenticationGUI()
        self.gui.create_layout(self.on_submit)
        
    def on_submit(self,**kwargs):
        self.validator_name = kwargs['validator_name']
        self.gui.app.closeAllWindows()
        return True
    
