from PyQt5.QtWidgets import QPushButton, QStatusBar, QLabel
from pprint import pprint

class Actions:
    def __init__(self, filters_object, display_object) -> None:
        self.filters_object = filters_object
        self.display_object = display_object
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

        old_changed_data = list(filter(lambda bbox:bbox.is_changed,self.display_object.old_bboxes))
        self.process_bboxes(old_changed_data)
        
        print("new     :",self.display_object.created_bboxes)
        print("old     :",old_changed_data)
        print("removed :",self.display_object.removed_bboxes)        
        
        self.display_object.change_next_image()
        self.widgets['status_bar'].clearMessage()
        self.widgets['status_bar'].showMessage("Approved")

    def process_bboxes(self,old_bboxes):
        current_position = self.display_object.current_position
        width,height = self.display_object.current_size

        for bbox in old_bboxes:
            new_coords = [
                bbox.rect().left()/width,
                bbox.rect().top()/height,
                bbox.rect().width()/width,
                bbox.rect().height()/height
            ]
            pprint(self.filters_object.data[current_position]['documents'][0]['img_data']['phone_results'][0])
        

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