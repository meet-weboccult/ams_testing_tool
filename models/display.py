from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QGraphicsScene, QGraphicsView,QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPen, QBrush, QImage, QTransform
from PyQt5.QtCore import Qt, QRectF
import requests
import numpy as np
import cv2
from pprint import pprint
class DrawableRectItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF(), pen=QPen(Qt.red, 3), brush=QBrush(Qt.NoBrush)):
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
        hover_pen = QPen(Qt.blue, self.pen().width())  # Create a red pen with the same line width
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
        self.widgets['image_name'] = self.create_image_name()
        self.clipboard = QApplication.clipboard()
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

    def change_previous_image(self):
        if self.current_position == 0:
            return
        self.current_position -= 1
        self.on_image_change()

    def change_next_image(self):
        self.current_position += 1
        self.on_image_change()

    def create_image_name(self):
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.mousePressEvent = lambda event: self.clipboard.setText(label.text())
        return label
    
    def display_image(self, url):
        
        self.widgets['image_name'].setText(url)
        self.scene.clear()
        self.view.resetTransform()        
        pixmap = QPixmap()
        try:
            pixmap.loadFromData(requests.get(url).content)
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            return
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
        self.view.keyReleaseEvent = self.keyReleaseEvent
        self.view.wheelEvent = self.wheelEvent

        return self.view
    
    def wheelEvent(self,event):
        change = event.angleDelta().y()//120
        self.view.scale(1+change/10,1+change/10)
        self.view.centerOn(self.view.mapToScene(event.pos()))
    
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
        if not event.buttons() & Qt.LeftButton:
            return
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
        elif event.key() == Qt.Key_R:
            self.view.resetTransform()

        elif event.key() == Qt.Key_Q:
            for item in self.scene.items():
                if isinstance(item, QGraphicsPixmapItem):
                    self.og_pixmap = item.pixmap()
                    cv_image = self.pixmap2cv(item.pixmap())
                    cv_image = self.dim_image(cv_image)
                    pixmap = self.cv2pixmap(cv_image)
                    item.setPixmap(pixmap)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Q:
            for item in self.scene.items():
                if isinstance(item, QGraphicsPixmapItem):
                    item.setPixmap(self.og_pixmap)

    def get_boundig_boxes(self):
        bboxes = []
        for bbox in self.created_bboxes:
            x1,y1,x2,y2 = bbox.rect().getCoords()
            bboxes.append([int(x1),int(y1),int(x2),int(y2)])
        for bbox in self.old_bboxes:
            x1,y1,x2,y2 = bbox.rect().getCoords()
            bboxes.append([int(x1),int(y1),int(x2),int(y2)])
        return bboxes

    def dim_image(self, cv_image):
        # Dim the image by 50%
        mask = np.zeros(cv_image.shape, dtype=np.uint8) 
        rois = {}
        for bbox in self.get_boundig_boxes():
            x1,y1,x2,y2 = bbox
            roi = cv_image[y1:y2,x1:x2]
            rois[(x1,y1,x2,y2)] = roi

        cv2_im = cv_image.copy()
        cv2_im = cv2.addWeighted(cv2_im, 0.7, mask, 0.3, 0)
        # make image grayscale and repeat channel 3 times
        cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2GRAY).repeat(3).reshape(cv2_im.shape)


        cv2_im = cv2.GaussianBlur(cv2_im, (21, 21), 0)
        for bbox in rois:
            x1,y1,x2,y2 = bbox
            cv2_im[y1:y2,x1:x2] = rois[bbox]
        return cv2_im
            

        

    def pixmap2cv(self,pixmap):
        buffer = pixmap.toImage().bits().asstring(pixmap.width()*pixmap.height()*4)
        arr = np.frombuffer(buffer, dtype=np.uint8).reshape((pixmap.height(), pixmap.width(), 4))
        img_bgr = arr[:, :, :3]
        return img_bgr
            
    def cv2pixmap(self, cv_image):
        h, w, ch = cv_image.shape
        bytesPerLine = ch * w
        return QPixmap(QImage(cv_image.data, w, h, bytesPerLine, QImage.Format_RGB888).rgbSwapped())
                
        
        
        
        