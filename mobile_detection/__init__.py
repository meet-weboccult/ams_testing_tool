from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QShortcut
import sys
from pprint import pprint
from .database_manager import Database
from .filters import Filters
from .display import Display
from .actions import Actions


class MobileDetection:
    def __init__(self) -> None:
        self.database_manager = Database()
        self.app = QApplication(sys.argv)
        self.window = self.create_window()
        self.filters = Filters(self.changed_filters)
        self.is_data_loaded = False
        self.display = Display(self.changed_image)
        self.actions = Actions(self.filters,self.display)
        self.place_widgets()
        self.set_shortcuts()
        self.show_window()
    
    def changed_filters(self,**kwargs):
        if not len(self.filters.data):
            self.display.scene.clear()
            self.actions.change_counter()
            return
        
        self.is_data_loaded = True
        self.display.current_position = 0
        self.actions.change_counter()
    
        first = self.filters.data[0]
        self.display.display_image(first['_id'])
        if self.display.imaged_loaded:
            self.display.draw_bboxes(first['documents'])
        else:
            self.actions.widgets['status_bar'].showMessage("CONNECTION ERROR:couln't load image")         

    def changed_image(self):
        position = self.display.current_position 
        total_images = len(self.filters.data)
        
        if not total_images: 
            self.actions.widgets['status_bar'].showMessage("No Images Found")
            return
        elif position >= total_images:
            self.actions.widgets['status_bar'].showMessage("End of Images")
            self.display.scene.clear()
            return
        
        image_data = self.filters.data[position]
        self.display.display_image(image_data['_id'])
        if self.display.imaged_loaded:
            self.display.draw_bboxes(image_data['documents'])
        else:
            self.actions.widgets['status_bar'].showMessage("CONNECTION ERROR:couln't load image")         
        self.actions.change_counter()

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
        col = QVBoxLayout()
        col.addWidget(self.display.widgets['image_name'])
        col.addWidget(self.display.widgets['display'])
        row2.addLayout(col)
        row2.addWidget(self.display.widgets['next_btn'])

        row3 = QHBoxLayout()
        row3.addWidget(self.actions.widgets['skip_btn'])
        row3.addWidget(self.actions.widgets['approve_btn'])
                        
        self.layout.addLayout(row1)
        self.layout.addStretch()
        self.layout.addLayout(row2)
        self.layout.addStretch()
        self.layout.addLayout(row3)          
        self.layout.addStretch()
        self.layout.addWidget(self.actions.widgets['status_bar'])
        self.layout.addStretch()
        
    def set_shortcuts(self):
        
        shortcut_next = QShortcut("Right",self.window)
        shortcut_next.activated.connect(self.display.change_next_image)

        shortcut_previous = QShortcut("Left",self.window)
        shortcut_previous.activated.connect(self.display.change_previous_image)

        shortcut_next = QShortcut("Ctrl+Right",self.window)
        shortcut_next.activated.connect(self.actions.skip)

        shortcut_previous = QShortcut("Ctrl+S",self.window)
        shortcut_previous.activated.connect(self.actions.approve)

    def show_window(self):
        self.window.setLayout(self.layout)
        self.window.show()
        self.app.exec_()
