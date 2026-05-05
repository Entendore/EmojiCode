"""Control panel with buttons, speed slider, and example selector."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal


class ControlPanel(QWidget):
    step_clicked = Signal()
    run_clicked = Signal()
    auto_toggled = Signal()
    stop_clicked = Signal()
    reset_clicked = Signal()
    example_load_requested = Signal(str)
    speed_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.setSpacing(6)

        # Speed control row
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(8)

        speed_label = QLabel("⏱️ Speed:")
        speed_label.setFixedWidth(60)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.setFixedWidth(130)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)

        self.speed_value_label = QLabel("51ms")
        self.speed_value_label.setFixedWidth(45)
        self.speed_value_label.setStyleSheet("color: #4fc1ff; font-family: Consolas;")

        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)
        speed_layout.addStretch()

        # Example selector
        self.example_combo = QComboBox()
        self.example_combo.addItems([
            "Binary Incrementer",
            "Math: Binary Decrementer",
            "Game: Rock-Paper-Scissors",
            "Output: ASCII Box Maker",
            "Output: Inventory Filter",
            "Output: Battle Logger"
        ])
        self.example_combo.setFixedWidth(200)

        btn_load = QPushButton("📋 Load")
        btn_load.setFixedWidth(70)
        btn_load.clicked.connect(self._on_load_clicked)

        speed_layout.addWidget(self.example_combo)
        speed_layout.addWidget(btn_load)
        main_layout.addLayout(speed_layout)

        # Main button row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.btn_step = QPushButton("▶️ Step")
        self.btn_run = QPushButton("⏩ Run All")
        self.btn_auto = QPushButton("🔁 Auto Run")
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_reset = QPushButton("🔄 Reset")

        self.btn_stop.setEnabled(False)

        # Set button tooltips
        self.btn_step.setToolTip("Execute one step (F10)")
        self.btn_run.setToolTip("Run to completion (F5)")
        self.btn_auto.setToolTip("Toggle auto-run (F6)")
        self.btn_stop.setToolTip("Stop auto-run (Escape)")
        self.btn_reset.setToolTip("Reset machine (Ctrl+R)")

        self.btn_step.clicked.connect(self.step_clicked.emit)
        self.btn_run.clicked.connect(self.run_clicked.emit)
        self.btn_auto.clicked.connect(self.auto_toggled.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)

        btn_layout.addWidget(self.btn_step)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_auto)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        main_layout.addLayout(btn_layout)

        # Zoom controls row
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(6)

        zoom_label = QLabel("🔍 Tape Zoom:")
        zoom_label.setFixedWidth(85)

        self.btn_zoom_in = QPushButton("➕")
        self.btn_zoom_in.setFixedWidth(40)
        self.btn_zoom_out = QPushButton("➖")
        self.btn_zoom_out.setFixedWidth(40)
        self.btn_zoom_reset = QPushButton("↺ Reset")
        self.btn_zoom_reset.setFixedWidth(60)

        self.btn_zoom_in.setToolTip("Zoom in (Ctrl+Plus)")
        self.btn_zoom_out.setToolTip("Zoom out (Ctrl+Minus)")
        self.btn_zoom_reset.setToolTip("Reset zoom (Ctrl+0)")

        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.btn_zoom_reset)
        zoom_layout.addStretch()

        main_layout.addLayout(zoom_layout)

        # Initialize speed display
        self._on_speed_changed(self.speed_slider.value())

    def _on_speed_changed(self, value):
        interval = max(1, 101 - value)
        self.speed_value_label.setText(f"{interval}ms")
        self.speed_changed.emit(interval)

    def _on_load_clicked(self):
        self.example_load_requested.emit(self.example_combo.currentText())

    def set_auto_running(self, is_running):
        self.is_auto_running = is_running
        if is_running:
            self.btn_auto.setText("⏸️ Pause")
            self.btn_stop.setEnabled(True)
            self.btn_step.setEnabled(False)
            self.btn_run.setEnabled(False)
        else:
            self.btn_auto.setText("🔁 Auto Run")
            self.btn_stop.setEnabled(False)
            self.btn_step.setEnabled(True)
            self.btn_run.setEnabled(True)

    @property
    def is_auto_running(self):
        return self._is_auto_running

    @is_auto_running.setter
    def is_auto_running(self, value):
        self._is_auto_running = value