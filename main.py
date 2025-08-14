import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEPTAwatch")
        self.setGeometry(100, 100, 500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create label with auto-resizing text
        self.label = QLabel("Welcome to SEPTAwatch!", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Set initial font size
        self.update_font_size()
        
        # Connect resize event to font update
        self.resizeEvent = self.on_resize
        
        # Timer to debounce resize events
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_font_size)
    
    def on_resize(self, event):
        # Debounce resize events to avoid excessive font updates
        self.resize_timer.start(100)
        event.accept()
    
    def update_font_size(self):
        # Calculate appropriate font size based on window dimensions
        window_width = self.width()
        window_height = self.height()
        
        # Base font size calculation (adjust these values as needed)
        base_size = min(window_width // 20, window_height // 8)
        base_size = max(base_size, 12)  # Minimum font size
        
        # Create and apply font
        font = QFont()
        font.setPointSize(base_size)
        font.setBold(True)
        self.label.setFont(font)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())