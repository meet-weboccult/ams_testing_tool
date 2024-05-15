from PyQt5.QtWidgets import  *
from PyQt5.QtCore import Qt,QRectF, QDateTime
from PyQt5.QtGui import QPixmap,QPen,QBrush,QTransform
import sys
import requests
import time
import pprint
from database_manager import Database

class Filters:
    def __init__(self,on_changed_filters) -> None:
        self.widgets = dict()
        self.database_manager = Database.get_instance()
        self.on_changed_filters = on_changed_filters
        self.data = []
        self.widgets["office_filter"] = self.create_office_filter()
        self.widgets["floor_filter"] = self.create_floor_filter()
        
        if self.widgets['office_filter'].count():
            self.change_floors(self.widgets["office_filter"].itemText(0))

        self.widgets["start_datetime"] = self.create_datetime_filter()
        self.widgets["end_datetime"] = self.create_datetime_filter()
        self.widgets["filter_btn"] = self.create_filter_btn()
   
    def create_office_filter(self):
        combobox = QComboBox()
        office_names = self.database_manager.get_site_names()
        combobox.addItems(office_names)
        combobox.currentTextChanged.connect(self.change_floors)
        return combobox
    
    def change_floors(self,site_name):
        floors = self.database_manager.get_workspace_of_site(site_name)
        self.widgets["floor_filter"].clear()
        self.widgets["floor_filter"].addItems(floors)
    
    def create_floor_filter(self):
        combobox = QComboBox()
        return combobox

    def create_datetime_filter(self):
        datetime = QDateTimeEdit()
        datetime.setDateTime(QDateTime.currentDateTime())
        datetime.setCalendarPopup(True)
        return datetime
    
    def create_filter_btn(self):
        btn = QPushButton("Filter")
        btn.clicked.connect(lambda:self.filter_data())
        return btn
    
    def filter_data(self):
        filter = {
            "office" : self.widgets['office_filter'].currentText(),
            "floor" : self.widgets['floor_filter'].currentText(),
            "start_time" : self.widgets['start_datetime'].dateTime().toString(Qt.ISODate),
            "end_time" : self.widgets['end_datetime'].dateTime().toString(Qt.ISODate),
        }
        self.data = list(self.database_manager.get_images(filter))     
        self.on_changed_filters()
        

class DrawableRectItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF(), pen=QPen(Qt.white, 4), brush=QBrush(Qt.NoBrush)):
        super().__init__(rect)
        self.setPen(pen)
        self.setBrush(brush)
        

class Display:
    def __init__(self, on_image_change) -> None:
        self.widgets = dict()
        self.on_image_change = on_image_change
        self.widgets['previous_btn'] = self.create_navigation_btn("<",self.change_previous_image)
        self.widgets['next_btn'] = self.create_navigation_btn(">",self.change_next_image)

        self.widgets['display'] = self.create_image_display()
        self.start_pos = None
        self.rect_item = None
        self.rect_items = [] 
        self.current_position = 0

    def create_navigation_btn(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setFixedWidth(50)
        btn.setFixedHeight(70)
        return btn
    
    def display_image(self, url):
        self.scene.clear()
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(url).content)
        pixmap = pixmap.scaled(1100,1100,Qt.KeepAspectRatio)
        width,height = pixmap.width(),pixmap.height()
        self.view.setFixedSize(width+2,height+2)
        self.scene.addPixmap(pixmap)       

    def change_previous_image(self):
        if self.current_position == 0:
            return
        self.current_position -= 1
        self.on_image_change()

    def change_next_image(self):
        self.current_position += 1
        self.on_image_change()
    

    def create_image_display(self):
        self.scene = QGraphicsScene()     
        self.view = QGraphicsView()
        self.view.setFixedSize(1000,600)
        self.view.setScene(self.scene)
        self.view.show()

        self.view.mousePressEvent = self.mousePressEvent
        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mouseReleaseEvent = self.mouseReleaseEvent
        self.view.keyPressEvent = self.keyPressEvent 

        return self.view

    def mousePressEvent(self, event):
        scene_event = self.view.mapToScene(event.pos()) 

        if event.button() == Qt.LeftButton:
            item = self.scene.itemAt(scene_event, QTransform())
            if isinstance(item, DrawableRectItem):
                self.rect_item = item
                self.start_pos = scene_event
            else:
                self.start_pos = scene_event
                rect = QRectF(self.start_pos, self.start_pos)
                self.rect_item = DrawableRectItem(rect)
                self.scene.addItem(self.rect_item)
                self.rect_items.append(self.rect_item)

    def mouseMoveEvent(self, event):
        scene_event = self.view.mapToScene(event.pos())
        view_rect = self.view.mapToScene(self.view.rect()).boundingRect()

        if self.rect_item and event.buttons() & Qt.LeftButton:
            if isinstance(self.rect_item, DrawableRectItem):
                rect = QRectF(self.start_pos, scene_event).normalized()
                clamped_rect = rect.intersected(view_rect)
                self.rect_item.setRect(clamped_rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = None
            self.rect_item = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.rect_item:
                self.scene.removeItem(self.rect_item)
                self.rect_items.remove(self.rect_item)
                self.rect_item = None

class Actions:
    def __init__(self) -> None:
        self.widgets = dict()
        self.widgets['skip_btn'] = self.create_action_btn("Skip",self.approve)
        self.widgets['approve_btn'] = self.create_action_btn("Approve",self.approve)


    def create_action_btn(self, text, callback):
        btn = QPushButton(text)
        return btn
    
    def approve(self):
        print("Approve")
class MobileDetection:
    def __init__(self) -> None:
        self.database_manager = Database()
        self.app = QApplication(sys.argv)
        self.window = self.create_window()
        self.filters = Filters(self.changed_filters)
        self.display = Display(self.changed_image)
        self.actions = Actions()
        self.place_widgets()
        self.show_window()
    
    def changed_filters(self,**kwargs):
        if not len(self.filters.data):
            return
        
        first = self.filters.data[0]['_id']
        self.display.display_image(first)
        

    def changed_image(self):
        position = self.display.current_position 
        if not len(self.filters.data) : 
            return
        image_data = self.filters.data[position]
        self.display.display_image(image_data['_id'])

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