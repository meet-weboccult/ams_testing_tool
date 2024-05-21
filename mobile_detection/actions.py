from typing import Any
from PyQt5.QtWidgets import QPushButton, QStatusBar, QLabel
from pprint import pprint
from .database_manager import Database

class Actions:
    def __init__(self, filters_object, display_object) -> None:
        self.filters_object = filters_object
        self.display_object = display_object
        self.database_manager = Database.get_instance()
        self.widgets = dict()
        self.widgets['skip_btn'] = self.create_action_btn("Skip",self.skip)
        self.widgets['approve_btn'] = self.create_action_btn("Approve",self.approve)
        self.widgets['counter_label'] = self.create_status_label()
        self.widgets['validated'] = self.create_status_label()
        self.widgets['stats'] = self.create_status_label()
        self.widgets['status_bar'] = self.create_status_bar()

        self.changed_count = 0
        self.removed_count = 0
        self.created_count = 0

    def create_action_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.clicked.connect(callback)   
        return btn
    
    def create_status_label(self):
        label = QLabel()
        return label
    
    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.setFixedHeight(30)
        status_bar.addPermanentWidget(self.widgets['validated'])
        status_bar.addPermanentWidget(self.widgets['stats'])
        status_bar.addPermanentWidget(self.widgets['counter_label'])
        status_bar.setStyleSheet("background-color: lightgrey; color: black;")
        return status_bar
        
    def approve(self):   
        if not len(self.filters_object.data) : 
            return

        change_count, removed_count, new_count = self.count_bboxes()
        if not(change_count or removed_count or new_count):
            count = self.database_manager.approve_image(self.display_object.current_image)
            if count > 0:
                self.widgets['status_bar'].showMessage("Approved")
        else:
            corrected_bboxes = self.get_correct_bboxes()
            
            result = self.database_manager.reject_image(self.display_object.current_data,corrected_bboxes)
            if result > 0:
                self.widgets['status_bar'].showMessage("Corrected image")
                self.changed_count += change_count
                self.removed_count += removed_count
                self.created_count += new_count
                self.widgets['stats'].setText(f"changed: {self.changed_count}, removed: {self.removed_count}, created:{self.created_count} \t")
                index = self.display_object.current_position
                self.filters_object.data[index]['validated'] = True
        self.display_object.change_next_image()
        
    def count_bboxes(self):
        changed_bboxes = []
        for document,bboxes in self.display_object.old_bboxes.items():
            for bbox in bboxes:
                if bbox.is_changed:
                    changed_bboxes.append(bbox)
        
        old_changed = len(changed_bboxes)
        old_deleted = len(self.display_object.removed_bboxes)
        new_created = len(self.display_object.created_bboxes)
              
        return old_changed, old_deleted, new_created
            

    def get_correct_bboxes(self):

        def normalize_points(coords):
            x1,y1,x2,y2 = coords
            x1 = x1/width
            y1 = y1/height
            x2 = x2/width
            y2 = y2/height
            return [x1,y1,x2,y2]

        all_boxes = []
        width,height = self.display_object.current_size
        
        for bboxes in self.display_object.old_bboxes.values():
            for bbox in bboxes:
                coords = normalize_points(bbox.boundingRect().getCoords())
                all_boxes.append(coords)
        
        for bbox in self.display_object.created_bboxes:
            all_boxes.append(normalize_points(bbox.boundingRect().getCoords()))
        
        return all_boxes          

    
    def skip(self):
        if not len(self.filters_object.data) : 
            return
        self.display_object.change_next_image()
        self.widgets['status_bar'].clearMessage()
        self.widgets['status_bar'].showMessage("Skipped")

    def change_counter(self):
        self.widgets['status_bar'].clearMessage()
        if not len(self.filters_object.data) : 
            self.widgets['counter_label'].setText("0/0")
            self.widgets['status_bar'].showMessage("No Images Found")
            return
        self.widgets['counter_label'].setText(f"{self.display_object.current_position+1}/{len(self.filters_object.data)}")