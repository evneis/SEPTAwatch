"""SEPTAwatch desktop monitor for SEPTA real-time JSON APIs."""

from __future__ import annotations

import sys
from typing import Any, Callable

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from septa_api import Arrivals, SeptaClient, format_delay, route_has_issue, strip_html
from stations import api_name_from_choice, station_choices

METRO_ROUTES = ("L1", "B1", "M1", "T1", "T2", "T3", "T4", "T5", "G1", "D1", "D2")
REFRESH_MS = 30_000


class ApiWorker(QThread):
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn: Callable[[], Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fn = fn

    def run(self) -> None:
        try:
            self.succeeded.emit(self._fn())
        except Exception as exc:  # noqa: BLE001 — surface any fetch failure in the UI
            self.failed.emit(str(exc))


def _item(text: Any) -> QTableWidgetItem:
    item = QTableWidgetItem("" if text is None else str(text))
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item


def fill_table(table: QTableWidget, headers: list[str], rows: list[list[Any]]) -> None:
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            table.setItem(row_index, col_index, _item(value))
    table.resizeColumnsToContents()
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    if headers:
        table.horizontalHeader().setStretchLastSection(True)


class MainWindow(QMainWindow):
    def __init__(self, client: SeptaClient | None = None) -> None:
        super().__init__()
        self.client = client or SeptaClient()
        self._worker: ApiWorker | None = None

        self.setWindowTitle("SEPTAwatch")
        self.setGeometry(80, 80, 1200, 720)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._build_alerts_tab()
        self._build_train_view_tab()
        self._build_arrivals_tab()
        self._build_next_tab()
        self._build_bus_tab()
        self._build_metro_tab()
        self._build_elevator_tab()

        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel("Ready")
        status.addWidget(self.status_label)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(REFRESH_MS)
        self.refresh_timer.timeout.connect(self.refresh_current_tab)
        self.refresh_timer.start()

        self.tabs.currentChanged.connect(self.refresh_current_tab)
        self.refresh_current_tab()

    def _busy(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    def _run(self, fn: Callable[[], Any], on_success: Callable[[Any], None]) -> None:
        if self._busy():
            return
        self.status_label.setText("Loading SEPTA data…")
        worker = ApiWorker(fn, self)
        self._worker = worker

        def handle_success(payload: Any) -> None:
            on_success(payload)
            self.status_label.setText("Updated from www3.septa.org/api")

        def handle_error(message: str) -> None:
            self.status_label.setText(f"Error: {message}")

        worker.succeeded.connect(handle_success)
        worker.failed.connect(handle_error)
        worker.start()

    def refresh_current_tab(self) -> None:
        index = self.tabs.currentIndex()
        refreshers = [
            self.load_alerts,
            self.load_train_view,
            self.load_arrivals,
            self.load_next,
            self.load_buses,
            self.load_metro,
            self.load_elevators,
        ]
        refreshers[index]()

    def _toolbar(self, *widgets: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        for widget in widgets:
            row.addWidget(widget)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_current_tab)
        row.addWidget(refresh)
        row.addStretch()
        return row

    # --- Alerts ---

    def _build_alerts_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.issues_only = QCheckBox("Show only routes with alerts/advisories")
        self.issues_only.setChecked(True)
        self.issues_only.stateChanged.connect(self.load_alerts)
        self.alert_filter = QLineEdit()
        self.alert_filter.setPlaceholderText("Filter by route id, e.g. rr_route_cyn or bus_route_33")
        layout.addLayout(self._toolbar(self.issues_only, self.alert_filter))
        self.alerts_table = QTableWidget()
        layout.addWidget(self.alerts_table)
        self.tabs.addTab(tab, "Alerts")

    def load_alerts(self) -> None:
        route = self.alert_filter.text().strip() or None

        def fetch() -> list[dict[str, Any]]:
            return self.client.get_alerts(route)

        def show(rows: list[dict[str, Any]]) -> None:
            if self.issues_only.isChecked():
                rows = [row for row in rows if route_has_issue(row)]
            fill_table(
                self.alerts_table,
                ["Route", "Name", "Mode", "Alert", "Detour", "Suspended", "Updated", "Summary"],
                [
                    [
                        row.get("route_id"),
                        row.get("route_name") or row.get("route"),
                        row.get("mode"),
                        row.get("isalert"),
                        row.get("isdetour"),
                        row.get("issuspended") or row.get("issuppend"),
                        row.get("last_updated"),
                        strip_html(row.get("description") or row.get("alert")),
                    ]
                    for row in rows
                ],
            )

        self._run(fetch, show)

    # --- TrainView ---

    def _build_train_view_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        hint = QLabel("Live Regional Rail positions from /TrainView/index.php. late ≥ 998 means no GPS.")
        layout.addWidget(hint)
        layout.addLayout(self._toolbar())
        self.trains_table = QTableWidget()
        layout.addWidget(self.trains_table)
        self.tabs.addTab(tab, "Regional Rail")

    def load_train_view(self) -> None:
        def show(rows: list[dict[str, Any]]) -> None:
            fill_table(
                self.trains_table,
                ["Train", "Line", "From", "Dest", "Current", "Next", "Delay", "Track", "Service"],
                [
                    [
                        row.get("trainno"),
                        row.get("line"),
                        row.get("SOURCE"),
                        row.get("dest"),
                        row.get("currentstop"),
                        row.get("nextstop"),
                        format_delay(row.get("late")),
                        row.get("TRACK"),
                        row.get("service"),
                    ]
                    for row in rows
                ],
            )

        self._run(self.client.get_train_view, show)

    # --- Arrivals ---

    def _build_arrivals_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.station_combo = QComboBox()
        self.station_combo.setEditable(True)
        self.station_combo.addItems(station_choices())
        self.station_combo.setCurrentText("Suburban Station")
        self.arrival_count = QSpinBox()
        self.arrival_count.setRange(1, 20)
        self.arrival_count.setValue(8)
        layout.addLayout(self._toolbar(QLabel("Station"), self.station_combo, QLabel("Results"), self.arrival_count))
        self.arrivals_title = QLabel()
        self.arrivals_title.setFont(QFont("", 11, QFont.Weight.Bold))
        layout.addWidget(self.arrivals_title)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        north_box = QWidget()
        north_layout = QVBoxLayout(north_box)
        north_layout.addWidget(QLabel("Northbound"))
        self.north_table = QTableWidget()
        north_layout.addWidget(self.north_table)
        south_box = QWidget()
        south_layout = QVBoxLayout(south_box)
        south_layout.addWidget(QLabel("Southbound"))
        self.south_table = QTableWidget()
        south_layout.addWidget(self.south_table)
        splitter.addWidget(north_box)
        splitter.addWidget(south_box)
        layout.addWidget(splitter)
        self.tabs.addTab(tab, "Arrivals")

    def load_arrivals(self) -> None:
        try:
            station = api_name_from_choice(self.station_combo.currentText())
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return
        results = self.arrival_count.value()

        def fetch() -> Arrivals:
            return self.client.get_arrivals(station, results=results)

        def show(payload: Arrivals) -> None:
            self.arrivals_title.setText(payload.title)
            headers = ["Train", "Line", "Origin", "Dest", "Status", "Sched", "Track", "Next"]
            fill_table(
                self.north_table,
                headers,
                [
                    [
                        row.get("train_id"),
                        row.get("line"),
                        row.get("origin"),
                        row.get("destination"),
                        row.get("status"),
                        row.get("sched_time"),
                        row.get("track"),
                        row.get("next_station"),
                    ]
                    for row in payload.northbound
                ],
            )
            fill_table(
                self.south_table,
                headers,
                [
                    [
                        row.get("train_id"),
                        row.get("line"),
                        row.get("origin"),
                        row.get("destination"),
                        row.get("status"),
                        row.get("sched_time"),
                        row.get("track"),
                        row.get("next_station"),
                    ]
                    for row in payload.southbound
                ],
            )

        self._run(fetch, show)

    # --- Next to Arrive ---

    def _build_next_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.from_combo = QComboBox()
        self.to_combo = QComboBox()
        for combo in (self.from_combo, self.to_combo):
            combo.setEditable(True)
            combo.addItems(station_choices())
        self.from_combo.setCurrentText("Suburban Station")
        self.to_combo.setCurrentText("30th Street Station")
        self.next_count = QSpinBox()
        self.next_count.setRange(1, 20)
        self.next_count.setValue(5)
        layout.addLayout(
            self._toolbar(
                QLabel("From"),
                self.from_combo,
                QLabel("To"),
                self.to_combo,
                QLabel("Results"),
                self.next_count,
            )
        )
        self.next_table = QTableWidget()
        layout.addWidget(self.next_table)
        self.tabs.addTab(tab, "Next to Arrive")

    def load_next(self) -> None:
        try:
            start = api_name_from_choice(self.from_combo.currentText())
            end = api_name_from_choice(self.to_combo.currentText())
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return
        results = self.next_count.value()

        def fetch() -> list[dict[str, Any]]:
            return self.client.get_next_to_arrive(start, end, results)

        def show(rows: list[dict[str, Any]]) -> None:
            fill_table(
                self.next_table,
                ["Train", "Line", "Depart", "Arrive", "Delay", "Direct", "Connection"],
                [
                    [
                        row.get("orig_train"),
                        row.get("orig_line"),
                        row.get("orig_departure_time"),
                        row.get("orig_arrival_time") or row.get("term_arrival_time"),
                        row.get("orig_delay"),
                        "Yes" if row.get("isdirect") else "No",
                        row.get("Connection") or "",
                    ]
                    for row in rows
                ],
            )

        self._run(fetch, show)

    # --- Bus / trolley ---

    def _build_bus_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.bus_route = QLineEdit("33")
        self.bus_route.setPlaceholderText("Route number, e.g. 33 or 10")
        layout.addLayout(self._toolbar(QLabel("Route"), self.bus_route))
        self.bus_table = QTableWidget()
        layout.addWidget(self.bus_table)
        self.tabs.addTab(tab, "Bus / Trolley")

    def load_buses(self) -> None:
        route = self.bus_route.text().strip()
        if not route:
            self.status_label.setText("Enter a bus or trolley route")
            return

        def fetch() -> list[dict[str, Any]]:
            return self.client.get_transit_view(route)

        def show(rows: list[dict[str, Any]]) -> None:
            fill_table(
                self.bus_table,
                ["Vehicle", "Direction", "Destination", "Next stop", "Delay", "Seats", "Offset (sec)"],
                [
                    [
                        row.get("VehicleID") or row.get("label"),
                        row.get("Direction"),
                        row.get("destination"),
                        row.get("next_stop_name"),
                        format_delay(row.get("late")),
                        row.get("estimated_seat_availability"),
                        row.get("Offset_sec"),
                    ]
                    for row in rows
                ],
            )

        self._run(fetch, show)

    # --- Metro v2 ---

    def _build_metro_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.metro_route = QComboBox()
        self.metro_route.addItems(METRO_ROUTES)
        hint = QLabel("Metro v2 /v2/trips/. L1, B1, and M1 have no onboard GPS (delay 998 / status NO GPS).")
        layout.addWidget(hint)
        layout.addLayout(self._toolbar(QLabel("Route"), self.metro_route))
        self.metro_table = QTableWidget()
        layout.addWidget(self.metro_table)
        self.tabs.addTab(tab, "Metro")

    def load_metro(self) -> None:
        route_id = self.metro_route.currentText()

        def fetch() -> list[dict[str, Any]]:
            return self.client.get_metro_trips(route_id)

        def show(rows: list[dict[str, Any]]) -> None:
            fill_table(
                self.metro_table,
                ["Trip", "Headsign", "Direction", "Vehicle", "Delay", "Status", "Next stop"],
                [
                    [
                        row.get("trip_id"),
                        row.get("trip_headsign"),
                        row.get("direction_name") or row.get("direction_id"),
                        row.get("vehicle_id"),
                        format_delay(row.get("delay")),
                        row.get("status"),
                        row.get("next_stop_name"),
                    ]
                    for row in rows
                ],
            )

        self._run(fetch, show)

    # --- Elevators ---

    def _build_elevator_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.elevator_meta = QLabel()
        layout.addWidget(self.elevator_meta)
        layout.addLayout(self._toolbar())
        self.elevator_table = QTableWidget()
        layout.addWidget(self.elevator_table)
        self.tabs.addTab(tab, "Elevators")

    def load_elevators(self) -> None:
        def show(payload: dict[str, Any]) -> None:
            meta = payload.get("meta") or {}
            self.elevator_meta.setText(
                f"{meta.get('elevators_out', '?')} elevators out · updated {meta.get('updated', '')}"
            )
            fill_table(
                self.elevator_table,
                ["Line", "Station", "Elevator", "Message"],
                [
                    [
                        row.get("line"),
                        row.get("station"),
                        row.get("elevator"),
                        strip_html(row.get("message")),
                    ]
                    for row in payload.get("results") or []
                ],
            )

        self._run(self.client.get_elevator_outages, show)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
