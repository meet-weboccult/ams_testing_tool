from PyQt5.QtWidgets import QPushButton

class Actions:
    def __init__(self, display_object) -> None:
        self.widgets = dict()
        self.widgets['skip_btn'] = self.create_action_btn("Skip",self.skip)
        self.widgets['approve_btn'] = self.create_action_btn("Approve",self.approve)

    def create_action_btn(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)   
        return btn
    
    def approve(self):
        print("Approve")

    def skip(self):
        print("Skip")