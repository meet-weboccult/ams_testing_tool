from PyQt5.QtWidgets import  *
from PyQt5.QtCore import Qt,QRectF, QDateTime, QDate, QTime
from PyQt5.QtGui import QPixmap,QPen,QBrush,QTransform
import sys
import requests
import time
from pprint import pprint
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

        self.widgets["start_datetime"] = self.create_datetime_filter(QDate().currentDate().addDays(-1))
        self.widgets["end_datetime"] = self.create_datetime_filter(QDate().currentDate())
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

    def create_datetime_filter(self,qdate):
        datetime = QDateTimeEdit()
        datetime.setDateTime(QDateTime(qdate,QTime()))
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
        self.initial_pen = pen  # Store the initial pen
        self.is_hovering = False  # Track hover state
        self.is_createing = True
        self.offset = []
    
    def hoverEnterEvent(self, event):
        self.is_hovering = True
        hover_pen = QPen(Qt.red, self.pen().width())  # Create a red pen with the same line width
        self.setPen(hover_pen)
    
    def hoverLeaveEvent(self, event):
        self.is_hovering = False
        self.setPen(self.initial_pen)  # Restore the initial pen

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
        self.current_size = []

    def create_navigation_btn(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setFixedWidth(50)
        btn.setFixedHeight(70)
        return btn
    
    def display_image(self, url):
        
        self.scene.clear()
        pixmap = QPixmap()
        try:
            pixmap.loadFromData(requests.get(url).content)
        except requests.exceptions.ConnectionError:
            print("Retrying")
            self.display_image(url)
        pixmap = pixmap.scaled(1100,1100,Qt.KeepAspectRatio)
        width,height = pixmap.width(),pixmap.height()
        if width == 0 or height == 0:
            print("Image Not found")
            return
        self.current_size = [width,height]
        self.view.setFixedSize(width+2,height+2)
        self.scene.addPixmap(pixmap)       

    def draw_bboxes(self, documents):
        
        for document in documents:
            for phone in document['img_data']['phone_results']:
                bbox = phone['bbox']
                x1 = round(bbox[0]*self.current_size[0])
                y1 = round(bbox[1]*self.current_size[1])
                w = round(bbox[2]*self.current_size[0]) - x1
                h = round(bbox[3]*self.current_size[1]) - y1

                rect = QRectF(x1,y1,w,h)
                rect_item = DrawableRectItem(rect)
                self.scene.addItem(rect_item)
                self.rect_items.append(rect_item)
        self.view.setFocus()

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
                # If there's already bbox present
                self.rect_item = item
                self.start_pos = scene_event
                self.rect_item.hoverEnterEvent(event)
                self.rect_item.is_createing = False
                self.rect_item.offset = [event.pos().x()-self.rect_item.rect().x(), 
                                         event.pos().y()-self.rect_item.rect().y() ]                    
            else:                                   
                # create New DrawableRectItem Object
                self.start_pos = scene_event
                rect = QRectF(self.start_pos, self.start_pos)
                self.rect_item = DrawableRectItem(rect)
                self.scene.addItem(self.rect_item)
                self.rect_items.append(self.rect_item)
            

    def mouseMoveEvent(self, event):

        if self.rect_item.is_createing:
            # creating new bbox
            scene_event = self.view.mapToScene(event.pos())
            view_rect = self.view.mapToScene(self.view.rect()).boundingRect()

            if self.rect_item and event.buttons() & Qt.LeftButton:
                if isinstance(self.rect_item, DrawableRectItem):
                    rect = QRectF(self.start_pos, scene_event).normalized()
                    clamped_rect = rect.intersected(view_rect)
                    self.rect_item.setRect(clamped_rect)
        else:
            # Moving bbox
            new_position = [event.pos().x()-self.rect_item.offset[0],
                            event.pos().y()-self.rect_item.offset[1]]
            self.rect_item.setRect(QRectF(new_position[0],new_position[1],self.rect_item.rect().width(),self.rect_item.rect().height()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.rect_item is not None:
                self.rect_item.hoverLeaveEvent(event)
            self.start_pos = None
            self.rect_item = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.change_previous_image()
        elif event.key() == Qt.Key_Right:
            self.change_next_image()
        elif event.key() == Qt.Key_Delete:
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