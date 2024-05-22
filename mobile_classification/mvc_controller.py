from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QUrl,QObject
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from .mvc_model import Model


class Controller(QObject):
    def __init__(self, view):
        super().__init__()
        self.model = Model()
        self.view = view
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_image_response)

    def load_documents(self, start_date, end_date, site_name, workspace_name):
        self.model.load_documents_from_mongodb(start_date, end_date, site_name, workspace_name)
        self.update_image()

    def update_image(self):
        self.view.scene.clear()
        image_url = self.model.get_image_url()
        if image_url:
            request = QNetworkRequest(QUrl(image_url))
            self.network_manager.get(request)
        self.view.update_sidebar_text(self.model.get_image_data())

    def handle_image_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll()
            qimage = QImage.fromData(image_data)
            pixmap = QPixmap.fromImage(qimage)
            self.view.update_image(pixmap)
            bboxes = self.model.get_bboxes()
            self.view.draw_rectangle(bboxes,pixmap.width(),pixmap.height())
        else:
            QMessageBox.warning(self.view,"Error",f"Error: {reply.errorString()}")
        reply.deleteLater()

    def show_previous_image(self):
        
        if self.model.previous_image():
            self.update_image()
        
        else:
           QMessageBox.warning(self.view.window,"Error","Can't show previous image!")

    def show_next_image(self):
        
        if self.model.next_image():
            self.update_image()
        
        else:
           QMessageBox.warning(self.view.window,"Error","Can't show next image!")