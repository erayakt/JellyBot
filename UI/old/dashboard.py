import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QGroupBox, QStatusBar, QTabWidget, QFrame
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPalette
import pyqtgraph as pg
from config import (
    COLOR_BG, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_TEXT, STYLE_BUTTON, STYLE_FRAME,
    FONT_HEADER, FONT_TITLE, FONT_BODY
)
from utils import add_shadow
from canvas import OceanCubeCanvas
from data_generator import generate_mock_data

class OceanDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦑 JellyBot – Underwater Exploration")
        self.resize(1650, 900)
        self._setup_palette()
        self._init_state()
        self._build_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(400)

    def _setup_palette(self):
        pal = QPalette()
        # Backgrounds
        for role in (QPalette.Window, QPalette.Base, QPalette.AlternateBase):
            pal.setColor(role, COLOR_BG)
        # Text
        for role in (QPalette.WindowText, QPalette.ButtonText, QPalette.HighlightedText):
            pal.setColor(role, COLOR_TEXT)
        # Buttons & selection
        pal.setColor(QPalette.Button, QColor(20, 45, 65))
        pal.setColor(QPalette.Highlight, COLOR_PRIMARY)
        self.setPalette(pal)
        self.setStyleSheet(f"""
            QGroupBox:title {{ color:{COLOR_PRIMARY.name()}; }}
            QTabWidget::pane {{ border:0px; }}
            QTabBar::tab {{ background:{COLOR_BG.name()}; color:{COLOR_TEXT.name()}; padding:8px 20px; font-size:16pt; }}
            QTabBar::tab:selected {{ background:{COLOR_PRIMARY.name()}; }}
            {STYLE_FRAME}
        """
        )

    def _init_state(self):
        self.data_log = []
        self.running = False
        self.mission_time = 0
        self.MAX_POINTS = 300
        self.steps = []
        self.temp = []
        self.tds = []
        self.flex = []
        self.acc = {ax: [] for ax in 'XYZ'}
        self.gyro = {ax: [] for ax in 'XYZ'}

    def _build_ui(self):
        layout = QVBoxLayout(self)
        # header, controls, main grid, status bar as in original
        # ... (for brevity, replicate build_ui logic)
        pass

    def _tick(self):
        if not self.running:
            return
        # update mission_time, generate data, update plots & cube
        pass

    # implement _start, _stop, _save methods
