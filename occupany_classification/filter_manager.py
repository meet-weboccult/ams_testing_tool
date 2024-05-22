from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class filter_manager:
    def __init__(self, database_object, CHECK_FILTER_STATUS) -> None:
        self.database_object = database_object
        self.CHECK_FILTER_STATUS = CHECK_FILTER_STATUS
        self.filter = dict()
        self.inner_horizontal_box = QHBoxLayout()

    def build_workspace_combo_box(self, name, list_workspace):
        self.list_workspace = list_workspace
        self.filter[name] = self.horizontal_box(self.workspace_combo_box_function)

    def build_floor_combo_box(self, name, list_workspace):
        self.list_workspace = list_workspace
        self.filter[name] = self.horizontal_box(self.floor_combo_box_function)

    def build_date_time_box(self, name):
        self.filter[name] = self.horizontal_box(self.date_time_box)

    def build_push_button(self, name):
        self.name = name
        self.filter[name] = self.horizontal_box(self.push_button)

    def horizontal_box(self, feature):
        self.inner_horizontal_box.setSpacing(100)
        feature_address = feature()
        self.add_widget(feature_address)
        return feature_address

    def floor_combo_box_function(self):
        workspace_combo_box = QComboBox()
        for workspace in self.list_workspace:
            workspace_combo_box.addItem(workspace)
        return workspace_combo_box

    def workspace_combo_box_function(self):
        workspace_combo_box = QComboBox()
        for workspace in self.list_workspace:
            workspace_combo_box.addItem(workspace)
        workspace_combo_box.activated[str].connect(
            lambda: self.change_floor(self.filter["workspace"].currentText())
        )
        return workspace_combo_box

    def change_floor(self, workspace_name):
        self.filter["floor"].clear()
        self.unique_workspace_name = self.database_object.get_workspace_name(
            workspace_name
        )
        for floor in self.unique_workspace_name:
            self.filter["floor"].addItem(floor)

    def date_time_box(self):
        datetime_edit = QDateTimeEdit()
        datetime_edit.setDateTime(QDateTime.currentDateTime())
        datetime_edit.setCalendarPopup(True)
        return datetime_edit

    def push_button(self):
        filter_button = QPushButton(self.name)
        filter_button.clicked.connect(lambda: self.get_all_filter_value())
        return filter_button

    def get_all_filter_value(self):
        filter = {
            "office": self.filter["workspace"].currentText(),
            "floor": self.filter["floor"].currentText(),
            "start_time": self.filter["starting_time"].dateTime().toString(Qt.ISODate),
            "end_time": self.filter["ending_time"].dateTime().toString(Qt.ISODate),
        }

        self.filter_database_data = self.database_object.get_image(filter)
        self.CHECK_FILTER_STATUS()

    def add_widget(self, item):
        self.inner_horizontal_box.addWidget(item)

    def add_layout(self, horizontal_layout):
        horizontal_layout.addLayout(self.inner_horizontal_box)

class CustomPolygon(QGraphicsPolygonItem):
    def __init__(self, polygon=None,color=None,database_obj=None,image_data_id=None):
        super().__init__(polygon)
        self.color=color
        self.polygon = polygon
        self.database_object=database_obj
        self.image_data_id = image_data_id
        self.count_=0
        self.status=True
        self.check_status()
        
    def check_status(self):
        if self.count_%2==0:
            self.status=True
        else:
            self.status=False

    def mousePressEvent(self, event) -> None:
        
        self.count_=self.count_+1
        self.check_status()
        if self.color == Qt.red:
            self.color = Qt.green
            self.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        elif self.color == Qt.green:
            self.color = Qt.red
            self.setPen(QPen(Qt.red, 3, Qt.SolidLine))
 