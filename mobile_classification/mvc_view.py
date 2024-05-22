from PyQt5.QtWidgets import *
from .mvc_controller import Controller
from PyQt5.QtGui import  QKeySequence, QIcon, QPainter, QPen, QFont,QColor
from PyQt5.QtCore import Qt,QRectF,QDate,QTime,QDateTime
from bson import json_util

class View:
    def __init__(self,model_manager,app,validator_name):
        
        self.controller = Controller(self)
        self.model_manager = model_manager
        self.app = app
        self.validator_name = validator_name
        self.is_blurring = False
        self.window = QWidget()
        
        self.font = QFont("",35,2,False)
        self.font.setFamily('Times')
        self.font.setBold(True)
        self.document = None
        self.init_graphics()
        self.window.show()
                
    def init_graphics(self):
        self.setup_graphics()
        self.setup_attributes()
        self.setup_sidebar_list()
        self.setup_shortcuts()
        self.set_layout()
        self.connectSignalsSlots()
    
    def connectSignalsSlots(self):
        
        self.prev_button.clicked.connect(self.controller.show_previous_image)
        self.next_button.clicked.connect(self.controller.show_next_image)
        self.filter_date_button.clicked.connect(self.load_documents_from_mongodb)
        self.update_bbox_button.clicked.connect(self.update_bbox)
        self.approve_button.clicked.connect(self.approve_data)
        
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Escape), self.window).activated.connect(self.window.close)
        QShortcut(QKeySequence(Qt.Key_A), self.window).activated.connect(self.approve_data)
        
    def load_documents_from_mongodb(self):
        start_date = self.start_date.dateTime().toPyDateTime()
        end_date = self.end_date.dateTime().toPyDateTime()
        site_name = self.select_office_button.currentText()
        workspace_name = self.select_floor_button.currentText()

        self.controller.load_documents(start_date, end_date, site_name, workspace_name)

    def update_bbox(self):
        if self.controller.model.documents:
            self.document = self.controller.model.get_current_document()
            for item in self.document:
                if item['_id'] == self.controller.model.bbox_mappings[self.controller.view.bbox_button.currentText()]:
                    item['usage_type'] = self.classes_button.currentText()
                    break
            
            self.controller.view.update_sidebar_text(json_util.dumps(self.document, indent=8))      
        
        else:
            QMessageBox.warning(self.window,"Error","No data loaded!")
        
    def approve_data(self):

        if self.controller.approved:
            QMessageBox.information(self.window,"Info","Document already approved")
            return

        if self.controller.model.documents and self.document:
            if all('usage_type' in keys for keys in self.document):
                for item in self.document:
                    query = {'_id':item['_id']}
                    update = {'$set': {'usage_type': item['usage_type'], 'validated_by': self.validator_name}}
                    self.controller.model.collection.update_one(query,update)
            
                self.document = None
                self.controller.approved = True
            
            else:
                QMessageBox.warning(self.window,"Error","Please update all BBOXs before approving")
        
        else:
            QMessageBox.warning(self.window,"Error","Either data is not loaded or you clicked on Approve without updating BBOX")

    def setup_graphics(self):
        self.image_view = QGraphicsView()
        self.image_view.wheelEvent = self.wheelEvent
        self.image_view.mousePressEvent = self.mousePressEvent
        self.image_view.mouseMoveEvent = self.mouseMoveEvent
        self.image_view.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.scene = QGraphicsScene()
        self.image_view.setScene(self.scene)    
        self.image_view.setRenderHint(QPainter.Antialiasing)
        self.image_view.setRenderHint(QPainter.SmoothPixmapTransform)
 
    def wheelEvent(self, event):
        change = event.angleDelta().y()//120
        self.image_view.scale(1+change/10,1+change/10)
        self.image_view.centerOn(self.image_view.mapToScene(event.pos()))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_drag_pos = event.pos()
            self.image_view.setDragMode(QGraphicsView.ScrollHandDrag)
    def mouseMoveEvent(self, event):
        if self.image_view.dragMode() == QGraphicsView.ScrollHandDrag:
            delta = event.pos() - self.last_drag_pos
            self.last_drag_pos = event.pos()
            self.image_view.horizontalScrollBar().setValue(self.image_view.horizontalScrollBar().value() - delta.x())
            self.image_view.verticalScrollBar().setValue(self.image_view.verticalScrollBar().value() - delta.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.image_view.setDragMode(QGraphicsView.NoDrag)
    
    def setup_attributes(self):
        self.prev_button = self.create_button("Previous","darkGreen", "icons/left.png", None)
        self.next_button = self.create_button("Next","darkGreen", "icons/right.png", None)
        
        self.select_floor_button = self.create_button("Select Floor", "darkMagenta", None, "combo")
        self.select_floor_button.addItems(['4th floor', '6th floor', '7th Floor', 'Workspace-1'])
        
        self.select_office_button = self.create_button("Select Office", "darkMagenta", None, "combo")
        self.select_office_button.addItems(["Elsner Iffco", "WOT"])
        
        self.start_date = QDateTimeEdit()
        self.start_date.setDisplayFormat("dd-MM-yyyy HH:mm:ss")
        self.start_date.setDateTime(QDateTime(QDate().currentDate().addDays(-10),QTime().currentTime()))
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateTimeEdit()
        self.end_date.setDisplayFormat("dd-MM-yyyy HH:mm:ss")
        self.end_date.setDateTime(QDateTime(QDate().currentDate(),QTime().currentTime()))
        self.end_date.setCalendarPopup(True)
        
        self.filter_date_button = self.create_button("Filter", "darkCyan", "icons/filter.png", None)
        
        self.approve_button = self.create_button("Approve (A)", "green", "icons/check-mark.png", None)
        self.bbox_button = self.create_button("Select BBOX", "darkRed", None, "combo")
        self.classes_button = self.create_button("Select Class", "darkGreen", None, "combo")
        self.classes_button.addItems(["in-hand", "not-in-hand"])
        
        self.update_bbox_button = self.create_button("Update BBOX (U)", "darkGreen", None, None)

    def create_button(self, text, bg_color, icon_path, type):
        if type is None:
            button = QPushButton(text)
        elif type == "combo":
            button = QComboBox()

        button.setStyleSheet(f"background-color: {bg_color}; color: white;")

        if type is not None:
            return button

        button.setIcon(QIcon(icon_path))
        return button

    def setup_sidebar_list(self):
        self.sidebar_text_edit = QPlainTextEdit()
        self.sidebar_text_edit.setReadOnly(True)

    def setup_shortcuts(self):

        QShortcut(QKeySequence(Qt.Key_Right), self.window).activated.connect(self.controller.show_next_image)
        QShortcut(QKeySequence(Qt.Key_Left), self.window).activated.connect(self.controller.show_previous_image)
        QShortcut("Escape",self.window).activated.connect(self.on_window_change)
        QShortcut(QKeySequence(Qt.Key_B),self.window).activated.connect(self.set_focus_bbox)
    
    def set_focus_bbox(self):
        self.bbox_button.setFocus()

    def on_window_change(self):
        self.window.close()
        self.model_manager.window.show()

    def set_layout(self):
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_office_button)
        button_layout.addWidget(self.select_floor_button)
        button_layout.addWidget(self.start_date)
        button_layout.addWidget(self.end_date)
        button_layout.addWidget(self.filter_date_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        
        classification_layout = QHBoxLayout()
        classification_layout.addWidget(self.bbox_button)
        classification_layout.addWidget(self.classes_button)
        classification_layout.addWidget(self.update_bbox_button)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar_text_edit)
        sidebar_layout.addWidget(self.approve_button)
        sidebar_layout.addLayout(classification_layout)
        sidebar_layout.addStretch()
        sidebar_layout.setSpacing(20)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_view)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(central_widget)
        splitter.setSizes([308, 600])

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(splitter)

        widget = QWidget()
        widget.setLayout(layout)
        self.window.setLayout(layout)

    def update_image(self, pixmap):
        
        pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(pixmap_item)
        pixmap_item.setPixmap(pixmap)
        self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)

    def update_sidebar_text(self, text):
        self.sidebar_text_edit.setPlainText(text)

    def draw_rectangle(self,bboxes,w,h):
        
        self.bbox_button.clear()
        for idx, coords in enumerate(bboxes):
            if coords[0] < 1:
                coords[0] = int(coords[0] * w)
            if coords[1] < 1:
                coords[1] = int(coords[1] * h)
            if coords[2] < 1:
                coords[2] = int(coords[2] * w)
            if coords[3] < 1:
                coords[3] = int(coords[3] * h)
            rect = QRectF(coords[0],coords[1],coords[2]-coords[0],coords[3]-coords[1])
            rect_item=QGraphicsRectItem(rect)
            rect_item.setPen(QPen(Qt.yellow,6))
            text_item = QGraphicsTextItem(f"Box-{idx+1}")
            text_item.setDefaultTextColor(QColor(255, 255, 0))
            text_item.setFont(self.font)
            text_item.setPos(coords[0],coords[1]-80)  # Set the position of the text item
            self.scene.addItem(text_item)
            self.scene.addItem(rect_item)
            self.bbox_button.addItem(f"Box-{idx+1}")
            self.controller.model.bbox_mappings[f"Box-{idx+1}"] = self.controller.model.get_current_document()[idx].get("_id",None)