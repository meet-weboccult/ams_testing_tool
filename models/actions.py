from PyQt5.QtWidgets import QPushButton, QStatusBar, QLabel
from pprint import pprint
from database_manager import Database

class Actions:
    def __init__(self, filters_object, display_object) -> None:
        self.filters_object = filters_object
        self.display_object = display_object
        self.database_manager = Database.get_instance()
        self.widgets = dict()
        self.widgets['skip_btn'] = self.create_action_btn("Skip",self.skip)
        self.widgets['approve_btn'] = self.create_action_btn("Approve",self.approve)
        self.widgets['counter_label'] = self.create_counter_label()
        self.widgets['status_bar'] = self.create_status_bar()

    def create_action_btn(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.clicked.connect(callback)   
        return btn
    
    def create_counter_label(self):
        label = QLabel()
        return label
    
    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.setFixedHeight(30)
        status_bar.addPermanentWidget(self.widgets['counter_label'])
        status_bar.setStyleSheet("background-color: lightgrey; color: black;")
        return status_bar
        
    def approve(self):   
        if not len(self.filters_object.data) : 
            return
        
        approve_message = ""

        old_changed_data = list(filter(lambda bbox:True,self.display_object.old_bboxes))
        if len(old_changed_data)>0:
            self.process_bboxes(old_changed_data)
            approve_message += f"{len(old_changed_data)} Bboxes Changed "

        self.delete_old_bboxes(self.display_object.removed_bboxes)
        if len(self.display_object.removed_bboxes)>0:
            approve_message += f" {len(self.display_object.removed_bboxes)} Bboxes Removed "
        
        approve_message = "No changes required, Approved" if approve_message == "" else approve_message

        self.display_object.change_next_image()
        self.widgets['status_bar'].clearMessage()
        self.widgets['status_bar'].showMessage(approve_message)

    def process_bboxes(self,old_bboxes):
        current_position = self.display_object.current_position
        width,height = self.display_object.current_size

        for bbox in old_bboxes:
            x1,y1,x2,y2 = bbox.rect().getCoords()
            x1,y1,x2,y2 = x1/width,y1/height,x2/width,y2/height
            new_coords = [x1,y1,x2,y2]            
            self.filters_object.data[current_position]['documents'][0]['img_data']['phone_results'][0]['bbox'] = new_coords
            self.database_manager.update_bbox(self.filters_object.data[current_position]['documents'][0])
    
    def delete_old_bboxes(self,removed_bboxes):
        for bbox in removed_bboxes:
            self.database_manager.delete_bbox(bbox.data)
        

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