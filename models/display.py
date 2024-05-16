from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QPen,QBrush,QTransform
from PyQt5.QtCore import Qt, QRectF
import requests
from pprint import pprint
class DrawableRectItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF(), pen=QPen(Qt.white, 3), brush=QBrush(Qt.NoBrush)):
        super().__init__(rect)
        self.setPen(pen)
        self.setBrush(brush)
        self.initial_pen = pen  # Store the initial pen
        self.is_hovering = False  # Track hover state
        self.is_createing = True
        self.offset = []
        self.data = None
        self.is_changed = False
        self.is_created = True
    
    def hoverEnterEvent(self, event):
        self.is_hovering = True
        hover_pen = QPen(Qt.red, self.pen().width())  # Create a red pen with the same line width
        self.setPen(hover_pen)
    
    def hoverLeaveEvent(self, event):
        self.is_hovering = False
        self.setPen(self.initial_pen)  
class Display:
    def __init__(self, on_image_change) -> None:
        self.widgets = dict()
        self.on_image_change = on_image_change
        self.widgets['previous_btn'] = self.create_navigation_btn("<",self.change_previous_image)
        self.widgets['next_btn'] = self.create_navigation_btn(">",self.change_next_image)

        self.widgets['display'] = self.create_image_display()
        self.start_pos = None
        self.rect_item = None
        self.created_bboxes = [] 
        self.old_bboxes = []
        self.removed_bboxes = []
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
        self.old_bboxes = []
        self.created_bboxes = []
        self.removed_bboxes = []
        for document in documents:
            for phone in document['img_data']['phone_results']:
                bbox = phone['bbox']
                x1 = round(bbox[0]*self.current_size[0])
                y1 = round(bbox[1]*self.current_size[1])
                w = round(bbox[2]*self.current_size[0]) - x1
                h = round(bbox[3]*self.current_size[1]) - y1

                rect = QRectF(x1,y1,w,h)
                rect_item = DrawableRectItem(rect)
                rect_item.data = document
                rect_item.is_created = False
                self.scene.addItem(rect_item)
                self.old_bboxes.append(rect_item)
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
                self.created_bboxes.append(self.rect_item)
            

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
            self.rect_item.is_changed = True
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
        if event.key() == Qt.Key_Delete:
            if self.rect_item:
                self.scene.removeItem(self.rect_item)
                if self.rect_item.is_created:
                    self.created_bboxes.remove(self.rect_item)
                else:
                    self.old_bboxes.remove(self.rect_item)  
                    self.removed_bboxes.append(self.rect_item)

                self.rect_item = None

