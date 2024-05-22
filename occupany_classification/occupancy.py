from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
from .database_manager import *
from .filter_manager import *
from .image_manager import *
from .review_manager import *

class MainWindow(QWidget):
    def __init__(self,model_manager, app, validator_name):
        super().__init__()
        self.model_manager = model_manager
        self.app = app
        self.validator_name = validator_name
        self.database_object = Database_data(validator_name)
        self.database_object.connection()
        self.database_object.find_all_data()
        self.unique_site_name = self.database_object.find_unique("site_name")
        self.unique_workspace_name = self.database_object.get_workspace_name(
            self.unique_site_name[0]
        )
        self.filter_manager = filter_manager(
            self.database_object, self.CHECK_FILTER_STATUS
        )
        self.image_manager = image_manager(
            self.database_object, self.CHECK_BUTTON_STATUS
        )
        self.review_manager = review_manager(
            self.image_manager,
            self.CHECK_BUTTON_STATUS,
            self.database_object,
            self.image_manager.save_database,
        )

        self.widgetIMG = QLabel()
        self.pixmap = QPixmap()
        self.initUI()
        self.shortcut_event()

    def shortcut_event(self):
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+right"), self)
        self.save_shortcut.activated.connect(self.image_manager.save_database)
        self.next_button_shortcut = QShortcut(QKeySequence("right"), self)
        self.next_button_shortcut.activated.connect(
            self.image_manager.change_image_next
        )
        self.previous_button_shortcut = QShortcut(QKeySequence("left"), self)
        self.previous_button_shortcut.activated.connect(
            self.image_manager.change_image_previous
        )
        change_shortcut = QShortcut("Escape",self)
        change_shortcut.activated.connect(self.on_window_change)

    def on_window_change(self):
        self.close()
        self.model_manager.window.show()

    def CHECK_FILTER_STATUS(self):
        self.filter_data = self.filter_manager.filter_database_data
        img_data_list = []
        data_dic = {}
        if len(self.filter_data) == 0:
            return
        
        for i in self.filter_data[self.image_manager.key]["documents"]:
            data_dic = {"_id": i["_id"], "image_data": i["img_data"]}
            img_data_list.append(data_dic)
        
        self.image_manager.image_display(
            self.filter_data[self.image_manager.key]["documents"][0]["image"],
            img_data_list,
        )

    def CHECK_BUTTON_STATUS(self):
        img_data_list = []
        for i in self.filter_data[self.image_manager.key]["documents"]:
            data_dic = {"_id": i["_id"], "image_data": i["img_data"]}
            img_data_list.append(data_dic)
        self.image_manager.image_display(
            self.filter_data[self.image_manager.key]["documents"][0]["image"],
            img_data_list,
        )

    def horizontal_box(self, number):
        horizontal_layout = QHBoxLayout(self)
        horizontal_layout.setSpacing(number)
        return horizontal_layout

    def vertical_box(self, number):
        vertical_layout = QVBoxLayout(self)
        vertical_layout.setSpacing(number)
        return vertical_layout

    def initUI(self):

        vertical_box = self.vertical_box(10)

        filter_horizontal_layout = self.horizontal_box(10)
        self.filter_manager.build_workspace_combo_box(
            "workspace", self.unique_site_name
        )

        self.filter_manager.build_floor_combo_box("floor", self.unique_workspace_name)
        self.filter_manager.build_date_time_box("starting_time")
        self.filter_manager.build_date_time_box("ending_time")
        self.filter_manager.build_push_button("filter")
        self.filter_manager.add_layout(filter_horizontal_layout)
        vertical_box.addLayout(filter_horizontal_layout)

        image_manager_layout = self.horizontal_box(10)
        self.image_manager.build_previous_push_button("<")
        self.image_manager.build_image("image")
        self.image_manager.build_next_push_button(">")
        self.image_manager.add_layout(image_manager_layout)
        vertical_box.addLayout(image_manager_layout)

        review_manager_layout = self.horizontal_box(10)
        self.review_manager.build_skip_button("skip")
        self.review_manager.build_validate_button("validate")
        self.review_manager.add_layout(review_manager_layout)
        vertical_box.addLayout(review_manager_layout)

        self.setWindowTitle("occupancy classification")
        self.show()
