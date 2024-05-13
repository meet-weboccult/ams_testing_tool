
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys


class MobileDetection:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.create_window()
        self.create_filters()
        self.create_image_display()
        self.show_window()

    def create_window(self):
        self.window = QWidget()
        self.window.setWindowTitle("Mobile Detection")
        screen = self.app.primaryScreen()
        size = screen.availableGeometry()
        self.window.setFixedSize(size.width(),size.height())

        self.layout = QVBoxLayout()
    
    def create_filters(self):
        filters_container = QHBoxLayout()

        office_filter = QComboBox()
        office_filter.addItems(["Elsner", "WOT"])
        office_filter.setFixedWidth(200)

        floor_filter = QComboBox()
        floor_filter.addItems(["floor 1", "floor 2"])
        floor_filter.setFixedWidth(200)

        time_filter_start = QDateTimeEdit()
        time_filter_start.setFixedWidth(200)

        to_label = QLabel(" To ")
        to_label.setFixedWidth(30)
        
        time_filter_end = QDateTimeEdit()
        time_filter_end.setFixedWidth(200)

        filter_btn = QPushButton("Filter")
        filter_btn.setFixedWidth(100)

        
        filters_container.addWidget(office_filter)
        filters_container.addWidget(floor_filter)
        filters_container.addWidget(time_filter_start)
        filters_container.addWidget(to_label)
        filters_container.addWidget(time_filter_end)
        filters_container.addWidget(filter_btn)

        filters_container.setAlignment(Qt.AlignLeft)


        self.layout.addLayout(filters_container)
      
    def create_image_display(self):
        display_container = QHBoxLayout()

        image_display = QLabel()
        pixmap = QPixmap("/home/wotmeet/Internship/meet-makwana-training-2024/tasks/qdrant/images/0f117fce-0a08-4f23-8b3f-c8a3c1265792_cat_image7.jpeg")
        image_display.setPixmap(pixmap)
        image_display.resize(pixmap.width(),pixmap.height())

        previous_btn = QPushButton("<")

        next_btn = QPushButton(">")

        display_container.addWidget(previous_btn)
        display_container.addWidget(image_display)
        display_container.addWidget(next_btn)


        self.layout.addLayout(display_container)


    def show_window(self):
        self.layout.setAlignment(Qt.AlignTop)
        self.window.setLayout(self.layout)
        self.window.show()

        self.app.exec_()
    
MobileDetection()