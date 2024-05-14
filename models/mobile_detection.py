from PyQt5.QtWidgets import  *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QImage,QBrush, QPen
import sys

class Filters:
    def __init__(self) -> None:
        self.widgets = dict()

        self.widgets["office_filter"] = self.create_office_filter()
        self.widgets["floor_filter"] = self.create_floor_filter()
        self.widgets["start_datetime"] = self.create_datetime_filter()
        self.widgets["end_datetime"] = self.create_datetime_filter()
        self.widgets["filter_btn"] = self.create_filter_btn()
   
    def create_office_filter(self):
        combobox = QComboBox()
        combobox.addItem("WOT")
        combobox.addItem("Elsner")
        return combobox
    
    def create_floor_filter(self):
        combobox = QComboBox()
        combobox.addItem("Floor 1")
        combobox.addItem("Floor 2")
        return combobox

    def create_datetime_filter(self):
        datetime = QDateTimeEdit()
        return datetime
    
    def create_filter_btn(self):
        btn = QPushButton("Filter")
        return btn

class Display:
    def __init__(self) -> None:
        self.widgets = dict()
        self.widgets['previous_btn'] = self.create_navigation_btn("<",self.change_previous_image)
        self.widgets['next_btn'] = self.create_navigation_btn(">",self.change_next_image)

        self.widgets['display'] = self.create_image_display()

    def create_navigation_btn(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setFixedWidth(50)
        btn.setFixedHeight(70)
        return btn

    def change_previous_image(self):
        pass

    def change_next_image(self):
        pass

    def create_image_display(self):
        self.scene = QGraphicsScene()     
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.show()
        
        return self.view

class MobileDetection:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.window = self.create_window()
        self.filters = Filters()
        self.display = Display()
        self.place_widgets()
        self.show_window()

    def create_window(self):
        window = QWidget()
        window.setWindowTitle("Mobile Detection")
        screen = self.app.primaryScreen()
        size = screen.availableGeometry()
        self.screen_size = (size.width(),size.height())
        window.setFixedSize(*self.screen_size)
        self.layout = QVBoxLayout()
        return window
    
    def place_widgets(self):
        row1 = QHBoxLayout()
        row1.addWidget(self.filters.widgets['office_filter'])
        row1.addWidget(self.filters.widgets['floor_filter'])
        row1.addWidget(self.filters.widgets['start_datetime'])
        row1.addWidget(self.filters.widgets['end_datetime'])
        row1.addWidget(self.filters.widgets['filter_btn'])

        row2 = QHBoxLayout()
        row2.addWidget(self.display.widgets['previous_btn'])
        row2.addWidget(self.display.widgets['display'])
        row2.addWidget(self.display.widgets['next_btn'])
                
        self.layout.addLayout(row1)
        self.layout.addLayout(row2)      
        
    def show_window(self):
        self.window.setLayout(self.layout)
        self.window.show()
        self.app.exec_()

MobileDetection()