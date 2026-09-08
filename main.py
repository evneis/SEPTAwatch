import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox, QVBoxLayout, QWidget


def resource_path(*parts: str) -> str:
    """Return a path to a bundled resource (works in source and PyInstaller builds)."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def load_app_icon() -> QIcon:
    """Prefer the platform-native icon when it exists, fall back to PNG."""
    ico_path = resource_path("philadelphia-septa-metro-logo.ico")
    png_path = resource_path("philadelphia-septa-metro-logo.png")
    if sys.platform == "win32" and os.path.exists(ico_path):
        return QIcon(ico_path)
    if os.path.exists(png_path):
        return QIcon(png_path)
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    return QIcon()


class MainWindow(QMainWindow):
    MIN_FONT_PT = 12
    MAX_FONT_PT = 48

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEPTAwatch")
        self.setMinimumSize(360, 280)
        self.resize(500, 400)

        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)

        self._build_menu()
        self._build_ui()

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_font_size)
        self.update_font_size()

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        quit_action = QAction("E&xit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)

        self.label = QLabel("Welcome to SEPTAwatch!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.subtitle = QLabel("Regional rail and transit monitor")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("color: palette(mid);")
        layout.addWidget(self.subtitle)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About SEPTAwatch",
            "SEPTAwatch is a desktop companion for SEPTA transit information.\n\n"
            "Live arrival tracking is not wired up yet.",
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_timer.start(100)

    def update_font_size(self):
        width = max(self.width(), 1)
        height = max(self.height(), 1)
        size = min(width // 20, height // 8)
        size = max(self.MIN_FONT_PT, min(size, self.MAX_FONT_PT))

        title_font = QFont()
        title_font.setPointSize(size)
        title_font.setBold(True)
        self.label.setFont(title_font)

        subtitle_font = QFont()
        subtitle_font.setPointSize(max(self.MIN_FONT_PT, size // 3))
        self.subtitle.setFont(subtitle_font)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SEPTAwatch")
    app.setOrganizationName("SEPTAwatch")
    app.setStyle("Fusion")

    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
