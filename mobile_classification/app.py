import sys
from mobile_classification import MobileClassification
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MobileClassification()
    window.show()
    sys.exit(app.exec_())