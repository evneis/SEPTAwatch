import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEPTAwatch")
        self.setGeometry(100, 100, 500, 400)

        label = QLabel("Welcome to SEPTAwatch!", self)
        label.move(50, 50)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())