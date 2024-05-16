from PyQt5.QtWidgets import QComboBox, QDateTimeEdit, QPushButton
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime

from database_manager import Database
class Filters:
    def __init__(self,on_changed_filters) -> None:
        self.widgets = dict()
        self.database_manager = Database.get_instance()
        self.on_changed_filters = on_changed_filters
        self.data = []
        self.widgets["office_filter"] = self.create_office_filter()
        self.widgets["floor_filter"] = self.create_floor_filter()
        
        if self.widgets['office_filter'].count():
            self.change_floors(self.widgets["office_filter"].itemText(0))

        self.widgets["start_datetime"] = self.create_datetime_filter(QDate().currentDate().addDays(-1))
        self.widgets["end_datetime"] = self.create_datetime_filter(QDate().currentDate())
        self.widgets["filter_btn"] = self.create_filter_btn()
   
    def create_office_filter(self):
        combobox = QComboBox()
        office_names = self.database_manager.get_site_names()
        combobox.addItems(office_names)
        combobox.currentTextChanged.connect(self.change_floors)
        return combobox
    
    def change_floors(self,site_name):
        floors = self.database_manager.get_workspace_of_site(site_name)
        self.widgets["floor_filter"].clear()
        self.widgets["floor_filter"].addItems(floors)
    
    def create_floor_filter(self):
        combobox = QComboBox()
        return combobox

    def create_datetime_filter(self,qdate):
        datetime = QDateTimeEdit()
        datetime.setDateTime(QDateTime(qdate,QTime()))
        datetime.setCalendarPopup(True)
        return datetime
    
    def create_filter_btn(self):
        btn = QPushButton("Filter")
        btn.clicked.connect(lambda:self.filter_data())
        return btn
    
    def filter_data(self):
        filter = {
            "office" : self.widgets['office_filter'].currentText(),
            "floor" : self.widgets['floor_filter'].currentText(),
            "start_time" : self.widgets['start_datetime'].dateTime().toString(Qt.ISODate),
            "end_time" : self.widgets['end_datetime'].dateTime().toString(Qt.ISODate),
        }
        self.data = list(self.database_manager.get_images(filter))     
        self.on_changed_filters()
        