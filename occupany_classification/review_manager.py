from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class review_manager:
    def __init__(
        self,
        image_manager_obj,
        CHECK_BUTTON_STATUS,
        database_object,
        save_database_function,
    ) -> None:
        self.filter = dict()
        self.inner_horizontal_box = QHBoxLayout()
        self.image_manager_obj = image_manager_obj
        self.CHECK_BUTTON_STATUS = CHECK_BUTTON_STATUS
        self.database_object = database_object
        self.save_database_function = save_database_function

    def build_skip_button(self, name):
        self.name = name
        self.filter[name] = self.horizontal_box(self.skip_button)

    def build_validate_button(self, name):
        self.name = name
        self.filter[name] = self.horizontal_box(self.validate_button)

    def horizontal_box(self, feature):
        self.inner_horizontal_box.setSpacing(100)
        feature_addresh = feature()
        self.add_widget(feature_addresh)
        return feature_addresh

    def skip_button(self):
        filter_button = QPushButton(self.name)
        filter_button.clicked.connect(self.skip_button_function)

        return filter_button

    def skip_button_function(self):
        self.image_manager_obj.key += 1
        self.CHECK_BUTTON_STATUS()

    def validate_button(self):
        filter_button = QPushButton(self.name)
        print("review_manager", self.save_database_function)
        filter_button.clicked.connect(self.validate_button_function)
        return filter_button

    def validate_button_function(self):
        self.image_manager_obj.key += 1
        self.CHECK_BUTTON_STATUS()
        self.save_database_function()

    def add_widget(self, item):
        print("add widget")
        self.inner_horizontal_box.addWidget(item)

    def add_layout(self, horizontal_layout):
        print("add_layout")
        horizontal_layout.addLayout(self.inner_horizontal_box)
