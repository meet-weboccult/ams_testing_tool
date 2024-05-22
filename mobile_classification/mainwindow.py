import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QMainWindow
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 300, 200)
        
        button1 = QPushButton('Open Window 1', self)
        button1.clicked.connect(self.open_window1)
        button1.setGeometry(50, 50, 200, 30)
        
        button2 = QPushButton('Open Window 2', self)
        button2.clicked.connect(self.open_window2)
        button2.setGeometry(50, 100, 200, 30)
        
        button3 = QPushButton('Open Window 3', self)
        button3.clicked.connect(self.open_window3)
        button3.setGeometry(50, 150, 200, 30)
        
    def open_window1(self):
        from mobile_classification import MobileClassification
        self.window1 = MobileClassification()
        self.window1.show()
        
    def open_window2(self):
        from mobile_classification import MobileClassification
        self.window1 = MobileClassification()
        self.window1.show()
        
    def open_window3(self):
        from mobile_classification import MobileClassification
        self.window1 = MobileClassification()
        self.window1.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())