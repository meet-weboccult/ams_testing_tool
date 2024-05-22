# from bson import json_util
# from PyQt5.QtWidgets import QMainWindow,QShortcut,QMessageBox,QWidget,QVBoxLayout,QApplication
# import sys
# from PyQt5.QtGui import  QKeySequence
# from PyQt5.QtCore import Qt
# from .mvc_controller import Controller
# class MobileClassification(QWidget):
#     def __init__(self, model_manager, app, validator_name):
#         super().__init__()
#         self.setWindowTitle("Mobile Classification")
#         self.setGeometry(0, 0, 1920, 1080)

#         self.controller = Controller()
#         self.document = None
#         self.validator_name = validator_name
        
#         self.initUI()
#         self.connectSignalsSlots()

#     def initUI(self):
#         # self.setCentralWidget(self.controller.view)
#         layout = QVBoxLayout()
#         layout.addWidget(self.controller.view)
#         self.setLayout(layout)
        
#     def connectSignalsSlots(self):
        
#         self.controller.view.prev_button.clicked.connect(self.controller.show_previous_image)
#         self.controller.view.next_button.clicked.connect(self.controller.show_next_image)
#         self.controller.view.filter_date_button.clicked.connect(self.load_documents_from_mongodb)
#         self.controller.view.update_bbox_button.clicked.connect(self.update_bbox)
#         self.controller.view.approve_button.clicked.connect(self.approve_data)
        
#         QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Escape), self).activated.connect(self.close)
        
#     def load_documents_from_mongodb(self):
#         start_date = self.controller.view.start_date.dateTime().toPyDateTime()
#         end_date = self.controller.view.end_date.dateTime().toPyDateTime()
#         site_name = self.controller.view.select_office_button.currentText()
#         workspace_name = self.controller.view.select_floor_button.currentText()

#         self.controller.load_documents(start_date, end_date, site_name, workspace_name)

#     def update_bbox(self):
#         if self.controller.model.documents:
#             self.document = self.controller.model.get_current_document()
#             for item in self.document:
#                 if item['_id'] == self.controller.model.bbox_mappings[self.controller.view.bbox_button.currentText()]:
#                     item['usage_type'] = self.controller.view.classes_button.currentText()
#                     break
            
#             self.controller.view.update_sidebar_text(json_util.dumps(self.document, indent=8))      
        
#         else:
#             QMessageBox.warning(self.controller.view,"Error","No data loaded!")
        
#     def approve_data(self):
#         if self.controller.model.documents and self.document:
#             for item in self.document:
#                 query = {'_id':item['_id']}
#                 update = {'$set': {'usage_type': item['usage_type'], 'validated_by': self.validator_name}}
#                 self.controller.model.collection.update_one(query,update)
        
#             self.document = None
#         else:
#             QMessageBox.warning(self.controller.view,"Error","Either data is not loaded or you clicked on Approve without updating BBOX")

from bson import json_util
from PyQt5.QtWidgets import QMainWindow,QShortcut,QMessageBox,QWidget,QVBoxLayout,QApplication
from PyQt5.QtGui import  QKeySequence
from PyQt5.QtCore import Qt
import sys
from .mvc_controller import Controller
class MobileClassification:
    def __init__(self,model_manager,app,validator):
        self.window= self.create_window()

        self.controller = Controller()
        self.document = None
        
        self.initUI()
        self.connectSignalsSlots()
        # self.window.show()
        
        
    def initUI(self):
        # self.setCentralWidget(self.controller.view)
        layout = QVBoxLayout()
        layout.addWidget(self.controller.view.window)
        self.window.setLayout(layout)
    
    def create_window(self):
        window = QWidget()
        window.setWindowTitle("Mobile Classification")
        window.setGeometry(0, 0, 1920, 1080)
        return window
        
    def connectSignalsSlots(self):
        
        self.controller.view.prev_button.clicked.connect(self.controller.show_previous_image)
        self.controller.view.next_button.clicked.connect(self.controller.show_next_image)
        self.controller.view.filter_date_button.clicked.connect(self.load_documents_from_mongodb)
        self.controller.view.update_bbox_button.clicked.connect(self.update_bbox)
        self.controller.view.approve_button.clicked.connect(self.approve_data)
        
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Escape), self.window).activated.connect(self.window.close)
        QShortcut(QKeySequence(Qt.Key_A), self.window).activated.connect(self.approve_data)
        QShortcut(QKeySequence(Qt.Key_U), self.window).activated.connect(self.update_bbox)
        
    def load_documents_from_mongodb(self):
        start_date = self.controller.view.start_date.dateTime().toPyDateTime()
        end_date = self.controller.view.end_date.dateTime().toPyDateTime()
        site_name = self.controller.view.select_office_button.currentText()
        workspace_name = self.controller.view.select_floor_button.currentText()

        self.controller.load_documents(start_date, end_date, site_name, workspace_name)

    def update_bbox(self):
        if self.controller.model.documents:
            self.document = self.controller.model.get_current_document()
            for item in self.document:
                if item['_id'] == self.controller.model.bbox_mappings[self.controller.view.bbox_button.currentText()]:
                    item['usage_type'] = self.controller.view.classes_button.currentText()
                    break
            
            self.controller.view.update_sidebar_text(json_util.dumps(self.document, indent=8))      
        
        else:
            QMessageBox.warning(self.controller.view,"Error","No data loaded!")
        
    def approve_data(self):
        if self.controller.model.documents and self.document:
            for item in self.document:
                query = {'_id':item['_id']}
                update = {'$set': {'usage_type': item['usage_type'], 'validated_by': self.controller.view.user_name}}
                self.controller.model.collection.update_one(query,update)
        
            self.document = None
        else:
            QMessageBox.warning(self.controller.view,"Error","Either data is not loaded or you clicked on Approve without updating BBOX")
