import sys
from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, 
                             QWidget, QHBoxLayout, QPushButton, QComboBox, 
                             QTextEdit, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from modules.api import SEPTAAPI, get_next_trains


class TrainDataThread(QThread):
    """Thread for fetching train data to avoid blocking the GUI."""
    data_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, from_station, to_station, num_results):
        super().__init__()
        self.from_station = from_station
        self.to_station = to_station
        self.num_results = num_results
    
    def run(self):
        try:
            api = SEPTAAPI()
            trains = api.get_next_to_arrive(self.from_station, self.to_station, self.num_results)
            self.data_ready.emit(trains)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEPTAwatch - Regional Rail Tracker")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize SEPTA API
        self.septa_api = SEPTAAPI()
        
        # Common station names for the dropdowns
        self.stations = [
            "Suburban Station", "30th Street Station", "Market East", 
            "Temple University", "University City", "Jefferson Station",
            "Penn Medicine", "Ardmore", "Bryn Mawr", "Paoli", "Thorndale",
            "Downingtown", "Exton", "Malvern", "Wayne", "Radnor", "Villanova", "Chelten Avenue"
        ]
        
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("SEPTA Regional Rail Tracker", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Station selection group
        station_group = QGroupBox("Select Route")
        station_layout = QGridLayout()
        
        # From station
        station_layout.addWidget(QLabel("From:"), 0, 0)
        self.from_station_combo = QComboBox()
        self.from_station_combo.addItems(self.stations)
        self.from_station_combo.setCurrentText("Suburban Station")
        station_layout.addWidget(self.from_station_combo, 0, 1)
        
        # To station
        station_layout.addWidget(QLabel("To:"), 1, 0)
        self.to_station_combo = QComboBox()
        self.to_station_combo.addItems(self.stations)
        self.to_station_combo.setCurrentText("30th Street Station")
        station_layout.addWidget(self.to_station_combo, 1, 1)
        
        # Number of results
        station_layout.addWidget(QLabel("Results:"), 2, 0)
        self.results_combo = QComboBox()
        self.results_combo.addItems(["5", "10", "15", "20"])
        self.results_combo.setCurrentText("10")
        station_layout.addWidget(self.results_combo, 2, 1)
        
        station_group.setLayout(station_layout)
        main_layout.addWidget(station_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.search_button = QPushButton("Search Trains")
        self.search_button.clicked.connect(self.search_trains)
        button_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("Auto-Refresh (30s)")
        self.refresh_button.setCheckable(True)
        self.refresh_button.clicked.connect(self.toggle_auto_refresh)
        button_layout.addWidget(self.refresh_button)
        
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        # Results display
        results_group = QGroupBox("Train Schedules")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(300)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # Status bar
        self.status_label = QLabel("Ready to search for trains")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def setup_timers(self):
        """Set up timers for auto-refresh functionality."""
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.search_trains)
        self.auto_refresh_interval = 30000  # 30 seconds
    
    def search_trains(self):
        """Search for trains between the selected stations."""
        from_station = self.from_station_combo.currentText()
        to_station = self.to_station_combo.currentText()
        num_results = int(self.results_combo.currentText())
        
        if from_station == to_station:
            self.results_text.setText("Error: Please select different stations for departure and arrival.")
            return
        
        self.status_label.setText(f"Searching for trains from {from_station} to {to_station}...")
        self.search_button.setEnabled(False)
        
        # Create and start the worker thread
        self.train_thread = TrainDataThread(from_station, to_station, num_results)
        self.train_thread.data_ready.connect(self.display_results)
        self.train_thread.error_occurred.connect(self.handle_error)
        self.train_thread.start()
    
    def display_results(self, trains):
        """Display the train results in the text area."""
        self.search_button.setEnabled(True)
        
        if not trains:
            self.results_text.setText("No trains found for the selected route.")
            self.status_label.setText("No trains found")
            return
        
        # Format the results
        from_station = self.from_station_combo.currentText()
        to_station = self.to_station_combo.currentText()
        
        result_text = f"Trains from {from_station} to {to_station}\n"
        result_text += f"Found {len(trains)} trains:\n"
        result_text += "=" * 60 + "\n\n"
        
        for i, train in enumerate(trains, 1):
            formatted_schedule = self.septa_api.format_train_schedule(train)
            result_text += f"{i}. {formatted_schedule}\n\n"
        
        self.results_text.setText(result_text)
        self.status_label.setText(f"Found {len(trains)} trains - Last updated: {self.get_current_time()}")
    
    def handle_error(self, error_message):
        """Handle errors from the API thread."""
        self.search_button.setEnabled(True)
        self.results_text.setText(f"Error occurred: {error_message}")
        self.status_label.setText("Error occurred")
    
    def toggle_auto_refresh(self, checked):
        """Toggle auto-refresh functionality."""
        if checked:
            self.auto_refresh_timer.start(self.auto_refresh_interval)
            self.refresh_button.setText("Auto-Refresh ON (30s)")
            self.status_label.setText("Auto-refresh enabled - searching every 30 seconds")
        else:
            self.auto_refresh_timer.stop()
            self.refresh_button.setText("Auto-Refresh (30s)")
            self.status_label.setText("Auto-refresh disabled")
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.clear()
        self.status_label.setText("Results cleared")
    
    def get_current_time(self):
        """Get current time as a formatted string."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def closeEvent(self, event):
        """Clean up when closing the application."""
        if hasattr(self, 'auto_refresh_timer'):
            self.auto_refresh_timer.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()