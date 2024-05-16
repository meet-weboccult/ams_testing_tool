from PyQt5.QtWidgets import  QApplication, QWidget, QVBoxLayout, QHBoxLayout, QShortcut
import sys
from pprint import pprint
from database_manager import Database
from filters import Filters
from display import Display
from actions import Actions


class MobileDetection:
    def __init__(self) -> None:
        self.database_manager = Database()
        self.app = QApplication(sys.argv)
        self.window = self.create_window()
        self.filters = Filters(self.changed_filters)
        self.display = Display(self.changed_image)
        self.actions = Actions(self.display)
        self.place_widgets()
        self.show_window()
    
    def changed_filters(self,**kwargs):
        if not len(self.filters.data):
            return
        
        first = self.filters.data[0]
        self.display.display_image(first['_id'])
        self.display.draw_bboxes(first['documents'])
        

    def changed_image(self):
        position = self.display.current_position 
        if not len(self.filters.data) : 
            return
        image_data = self.filters.data[position]
        self.display.display_image(image_data['_id'])
        self.display.draw_bboxes(image_data['documents'])

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

        row3 = QHBoxLayout()
        row3.addWidget(self.actions.widgets['skip_btn'])
        row3.addWidget(self.actions.widgets['approve_btn'])
                        
        self.layout.addLayout(row1)
        self.layout.addLayout(row2)
        self.layout.addLayout(row3)          

    def show_window(self):
        self.window.setLayout(self.layout)
        self.window.show()
        self.app.exec_()

MobileDetection()