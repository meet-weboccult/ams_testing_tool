from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QGraphicsScene, QGraphicsView,QGraphicsRectItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPen, QBrush, QImage, QTransform
from PyQt5.QtCore import Qt, QRectF
import requests
import numpy as np
import cv2

class DrawableRectItem(QGraphicsRectItem):
    def __init__(self, rect=QRectF(), pen=QPen(Qt.red, 3), brush=QBrush(Qt.NoBrush)):
        super().__init__(rect)
        self.setPen(pen)
        self.setBrush(brush)
        self.initial_pen = pen  
        self.is_hovering = False  
        self.is_createing = True
        self.offset = []
        self.data = None
        self.is_changed = False
        self.is_created = True
        self.parent_document = None
        self.index_in_document = None
    
    def hoverEnterEvent(self, event):
        self.is_hovering = True
        hover_pen = QPen(Qt.blue, self.pen().width())  
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
        self.current_rect = None

        self.old_bboxes = dict()
        self.created_bboxes = []
        self.removed_bboxes = dict()

        self.current_position = 0
        self.current_data = None
        self.current_size = []
        self.imaged_loaded = False

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
        self.current_image = url
        self.scene.clear()
        self.view.resetTransform()        
        pixmap = QPixmap()
        try:
            pixmap.loadFromData(requests.get(url).content)
            self.imaged_loaded = True
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            self.imaged_loaded = False
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
        self.old_bboxes = dict()
        self.created_bboxes = []
        self.removed_bboxes = dict()
        for document in documents:
            self.current_data = document
            for index,phone in enumerate(document['img_data']['phone_results']):
                bbox = phone['bbox']

                x1 = round(bbox[0]*self.current_size[0])
                y1 = round(bbox[1]*self.current_size[1])
                w = round(bbox[2]*self.current_size[0]) - x1
                h = round(bbox[3]*self.current_size[1]) - y1
                rect = QRectF(x1,y1,w,h)

                rect_item = DrawableRectItem(rect)
                rect_item.data = document
                rect_item.is_created = False
                rect_item.parent_document = document['_id']
                rect_item.index_in_document = index
                
                self.scene.addItem(rect_item)
                self.old_bboxes[document['_id']] = self.old_bboxes.get(document['_id'],[]) + [rect_item]
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
                self.current_rect = item
                self.start_pos = scene_event
                self.current_rect.hoverEnterEvent(event)
                self.current_rect.is_createing = False
                self.current_rect.offset = [event.pos().x()-self.current_rect.rect().x(), 
                                         event.pos().y()-self.current_rect.rect().y() ]                    
            else:                                   
                # create New DrawableRectItem Object
                self.start_pos = scene_event
                rect = QRectF(self.start_pos, self.start_pos)
                self.current_rect = DrawableRectItem(rect)
                self.scene.addItem(self.current_rect)
                self.created_bboxes.append(self.current_rect)
            

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return
        if self.current_rect.is_createing:
            # creating new bbox
            scene_event = self.view.mapToScene(event.pos())
            view_rect = self.view.mapToScene(self.view.rect()).boundingRect()

            if self.current_rect and event.buttons() & Qt.LeftButton:
                if isinstance(self.current_rect, DrawableRectItem):
                    rect = QRectF(self.start_pos, scene_event).normalized()
                    clamped_rect = rect.intersected(view_rect)
                    self.current_rect.setRect(clamped_rect)
        else:
            # Moving bbox
            self.current_rect.is_changed = True
            new_position = [event.pos().x()-self.current_rect.offset[0],
                            event.pos().y()-self.current_rect.offset[1]]
            self.current_rect.setRect(QRectF(new_position[0],new_position[1],self.current_rect.rect().width(),self.current_rect.rect().height()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.current_rect is not None:
                self.current_rect.hoverLeaveEvent(event)
            self.start_pos = None
            self.current_rect = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if self.current_rect:
                self.scene.removeItem(self.current_rect)
                parent_doc = self.current_rect.parent_document
                if self.current_rect.is_created:
                    self.created_bboxes.remove(self.current_rect)
                else:
                    self.old_bboxes[parent_doc].remove(self.current_rect)
                    self.removed_bboxes[parent_doc] = self.removed_bboxes.get(parent_doc,[]) + [self.current_rect]

                self.current_rect = None
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
        
        for document in self.old_bboxes:
            for bbox in self.old_bboxes[document]:
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
                
        
        
        
        