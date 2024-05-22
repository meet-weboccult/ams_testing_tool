from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import requests


class image_manager:

    def __init__(self, database_object, CHECK_BUTTON_STATUS) -> None:
        self.filter = dict()
        self.CHECK_BUTTON_STATUS = CHECK_BUTTON_STATUS
        self.inner_horizontal_box = QHBoxLayout()
        self.database_object = database_object
        self.widgetIMG = QLabel()
        self.pixmap = QPixmap()
        self.key = 0
        # self.item=None

    def save_database(self):
        for count in self.roi_values:
            id_ = count["_id"]
            self.item.update_database(id_,self.status_dic[id_].status)

    def build_next_push_button(self, name):
        self.name = name
        self.filter[name] = self.horizontal_box(self.next_push_button)

    def next_push_button(self):
        filter_button = QPushButton(self.name)
        filter_button.clicked.connect(lambda: self.change_image_next())
        return filter_button

    def build_previous_push_button(self, name):
        self.name = name
        self.filter[name] = self.horizontal_box(self.previous_push_button)

    def build_image(self, name):
        self.filter[name] = self.horizontal_box(self.image_box)

    def horizontal_box(self, feature):
        self.inner_horizontal_box.setSpacing(100)
        feature_address = feature()
        self.add_widget(feature_address)
        return feature_address

    def image_box(self):

        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.view.show()
        # self.image_display()
        return self.view

    def image_display(self, URL, roi_value):
        self.roi_values = roi_value
        self.scene.clear()
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(URL).content)
        pixmap = pixmap.scaledToHeight(600)
        self.scene.addPixmap(pixmap)
        self.status_dic={}
        for index, roi in enumerate(self.roi_values):
            store_all_points = roi["image_data"]["rois"][0]["points"]
            if roi["image_data"]["rois"][0]["status"] == "full":
                self.color = Qt.green
            elif roi["image_data"]["rois"][0]["status"] == "empty":
                self.color = Qt.red
            else:
                self.color = Qt.blue
            polygons = []
            roi_id = self.roi_values[index]["_id"]
            
            
            all_polygon_roi = roi["image_data"]["rois"][0]["points"]
            polygon = QPolygonF()
            for point in all_polygon_roi:
                x, y = point[0] * pixmap.width(), point[1] * pixmap.height()
                polygon.append(QPointF(x, y))

            polygons.append(polygon)
            for polygon in polygons:
                
                self.item = CustomPolygon(
                    polygon, self.color, self.database_object, roi_id
                )
                self.item.setPen(QPen(self.color, 3, Qt.SolidLine))
                self.scene.addItem(self.item)
                self.status_dic[roi_id]=self.item

    def previous_push_button(self):
        filter_button = QPushButton(self.name)
        filter_button.clicked.connect(lambda: self.change_image_previous())
        return filter_button

    def change_image_next(self):
        self.key = self.key + 1
        self.CHECK_BUTTON_STATUS()

    def change_image_previous(self):
        if self.key == 0:
            return
        else:
            self.key = self.key - 1
            self.CHECK_BUTTON_STATUS()

    def add_widget(self, item):
        self.inner_horizontal_box.addWidget(item)

    def add_layout(self, horizontal_layout):
        horizontal_layout.addLayout(self.inner_horizontal_box)


class CustomPolygon(QGraphicsPolygonItem):
    def __init__(self, polygon=None, color=None, database_obj=None, image_data_id=None,):
        super().__init__(polygon)

        self.color = color
        self.polygon = polygon
        self.database_object = database_obj
        self.image_data_id = image_data_id
        self.count_ = 0
        self.status = True

    def check_status(self):
        if self.count_ % 2 == 0:
            self.status = True
        else:
            self.status = False

    def mousePressEvent(self, event) -> None:
        self.count_ = self.count_ + 1
        self.check_status()
        if self.color == Qt.red:
            self.color = Qt.green
            self.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        elif self.color == Qt.green:
            self.color = Qt.red
            self.setPen(QPen(Qt.red, 3, Qt.SolidLine))

    def update_database(self, id_,status):
        self.id_ = id_
        self.database_object.update_date(
            self.id_, status
        )
