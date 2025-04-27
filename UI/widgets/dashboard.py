import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QGroupBox, QPushButton, QLabel, QFrame, QStatusBar
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from config import *
from utils.data import generate_mock_data
from utils.ui_helpers import add_shadow
from widgets.ocean_cube import OceanCubeCanvas
from PyQt5.QtGui import QFont, QColor, QPalette

# State
data_log = []
running = False
mission_time = 0
MAX_POINTS = 300

class OceanDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦑 JellyBot – Underwater Exploration")
        self.resize(1650, 900)
        self._setup_palette()
        self._init_buffers()
        self._build_ui()
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(400)

     # ------------------------------------------------------------------
    def _setup_palette(self):
        pal = QPalette()
        for role in (QPalette.Window, QPalette.Base, QPalette.AlternateBase): pal.setColor(role, COLOR_BG)
        for role in (QPalette.WindowText, QPalette.ButtonText, QPalette.HighlightedText): pal.setColor(role, COLOR_TEXT)
        pal.setColor(QPalette.Button, QColor(20,45,65)); pal.setColor(QPalette.Highlight, COLOR_PRIMARY)
        self.setPalette(pal)
        self.setStyleSheet(f"""
            QGroupBox:title {{ subcontrol-origin: margin; left: 6px; padding: 0 4px; color:{COLOR_PRIMARY.name()}; }}
            QTabWidget::pane {{ border:0px; }}
            QTabBar::tab {{ background:{COLOR_BG.name()}; color:{COLOR_TEXT.name()}; padding:8px 20px; font-size:16pt; }}
            QTabBar::tab:selected {{ background:{COLOR_PRIMARY.name()}; }}
            {STYLE_FRAME}
        """)

    # ------------------------------------------------------------------
    def _init_buffers(self):
        self.steps=[]; self.temp=[]; self.tds=[]; self.flex=[]
        self.acc={ax:[] for ax in 'XYZ'}; self.gyro={ax:[] for ax in 'XYZ'}

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # HEADER -------------------------------------------------------
        hdr_frame = QFrame(); hdr_layout = QVBoxLayout(hdr_frame); add_shadow(hdr_frame, blur=45, dy=6)
        hdr = QLabel("🌊 JellyBot Control Panel"); hdr.setFont(FONT_HEADER); hdr.setStyleSheet(f"color:{COLOR_PRIMARY.name()}")
        hdr.setAlignment(Qt.AlignCenter)
        hdr_layout.addWidget(hdr)
        layout.addWidget(hdr_frame)

        # CONTROLS -----------------------------------------------------
        ctrl_frame = QFrame(); ctrl_layout = QVBoxLayout(ctrl_frame)
        ctrl_grp = QGroupBox("Mission Control"); ctrl_grp.setFont(FONT_TITLE)
        h = QHBoxLayout()
        for text, func in [("▶ Start", self._start), ("⏹ Stop", self._stop), ("💾 Save", self._save)]:
            btn = QPushButton(text); btn.setFont(FONT_BODY); btn.setStyleSheet(STYLE_BUTTON); btn.clicked.connect(func); add_shadow(btn, blur=30, dy=4)
            h.addWidget(btn)
        ctrl_grp.setLayout(h); ctrl_layout.addWidget(ctrl_grp)
        add_shadow(ctrl_frame)
        layout.addWidget(ctrl_frame)

        # MAIN GRID ----------------------------------------------------
        main_frame = QFrame(); main_layout = QGridLayout(main_frame); add_shadow(main_frame, blur=35, dy=6)

        # numeric labels row
        lbl_container = QWidget(); lbl_h = QHBoxLayout(lbl_container)
        self.temp_lbl = QLabel(); self.tds_lbl = QLabel(); self.flex_lbl = QLabel()
        for w in (self.temp_lbl, self.tds_lbl, self.flex_lbl):
            w.setFont(FONT_BODY); w.setStyleSheet(f"color:{COLOR_TEXT.name()}; padding:4px 20px;")
            lbl_h.addWidget(w)
        main_layout.addWidget(lbl_container, 0, 0, 1, 2)

        # orientation cube with frame & shadow
        cube_frame = QFrame(); cube_layout = QVBoxLayout(cube_frame)
        self.cube = OceanCubeCanvas(self, w=5, h=5)
        cube_layout.addWidget(self.cube)
        add_shadow(cube_frame)
        main_layout.addWidget(cube_frame, 1, 1, 2, 1)

        # graph tabs section
        graph_frame = QFrame(); graph_layout = QVBoxLayout(graph_frame)
        graph_tabs = QTabWidget(); graph_tabs.setFont(FONT_TITLE)
        graph_tabs.addTab(self._build_env_sensor_tab(), "Env Sensors")
        graph_tabs.addTab(self._build_motion_tab(),      "Motion")
        graph_layout.addWidget(graph_tabs)
        add_shadow(graph_frame)
        main_layout.addWidget(graph_frame, 1, 0)

        layout.addWidget(main_frame)

        # STATUS BAR ---------------------------------------------------
        layout.addWidget(self._build_status_bar())

    # ------------------------------------------------------------------
    def _build_env_sensor_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.plot_temp = self._make_line_plot("Temp (°C)")
        self.plot_tds  = self._make_line_plot("TDS (ppm)")
        self.plot_flex = self._make_line_plot("Flex (V)")
        for p in (self.plot_temp, self.plot_tds, self.plot_flex): v.addWidget(p)
        return w

    def _build_motion_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.accel_plot = self._make_xyz_plot("Accel (m/s²)")
        self.gyro_plot  = self._make_xyz_plot("Gyro (°/s)")
        v.addWidget(self.accel_plot); v.addWidget(self.gyro_plot)
        return w

    # ------------------------------------------------------------------
    @staticmethod
    def _make_line_plot(title):
        p = pg.PlotWidget(title=title); p.setTitle(title, color=COLOR_TEXT.name(), size="12pt")
        p.getAxis('bottom').setPen(COLOR_TEXT.name()); p.getAxis('left').setPen(COLOR_TEXT.name())
        return p

    @staticmethod
    def _make_xyz_plot(title):
        p = pg.PlotWidget(title=title); p.setTitle(title, color=COLOR_TEXT.name(), size="12pt")
        p.getAxis('bottom').setPen(COLOR_TEXT.name()); p.getAxis('left').setPen(COLOR_TEXT.name())
        for clr in ('r','g','b'):
            p.plot([], [], pen=pg.mkPen(clr, width=2))
        return p

    # ------------------------------------------------------------------
    def _build_status_bar(self):
        bar = QStatusBar(); self.time_lbl = QLabel("00:00"); self.msg_lbl = QLabel("Ready")
        for w in (self.time_lbl, self.msg_lbl): w.setFont(FONT_BODY); w.setStyleSheet(f"color:{COLOR_TEXT.name()}")
        bar.addPermanentWidget(self.time_lbl); bar.addWidget(self.msg_lbl)
        return bar

    # ------------------------------------------------------------------
    def _start(self):
        global running, mission_time
        running, mission_time = True, 0; self.msg_lbl.setText("Running")

    def _stop(self):
        global running
        running = False; self.msg_lbl.setText("Paused")

    def _save(self):
        pd.DataFrame(data_log).to_csv("data.csv", index=False); self.msg_lbl.setText("Data saved to data.csv")

    # ------------------------------------------------------------------
    def _tick(self):
        global mission_time
        if not running: return

        mission_time += 0.4; m,s = divmod(int(mission_time),60); self.time_lbl.setText(f"{m:02d}:{s:02d}")
        d = generate_mock_data(); data_log.append(d); i = len(data_log)
        self.steps.append(i)
        self.temp.append(d['Temperature_C']); self.tds.append(d['TDS_ppm']); self.flex.append(d['Flex Voltage'])
        for ax in 'XYZ':
            self.acc[ax].append(d[f'Accel{ax}']); self.gyro[ax].append(d[f'Gyro{ax}'])
        if i > MAX_POINTS:
            for seq in (self.steps, self.temp, self.tds, self.flex): seq.pop(0)
            for dic in (self.acc, self.gyro):
                for ax in 'XYZ': dic[ax].pop(0)

        # numeric labels
        self.temp_lbl.setText(f"🌡 Temp: {d['Temperature_C']:.2f} °C")
        self.tds_lbl .setText(f"💧 TDS: {d['TDS_ppm']:.0f} ppm")
        self.flex_lbl.setText(f"📏 Flex: {d['Flex Voltage']:.2f} V")

        # env sensor plots
        for buf, plot, col in [(self.temp, self.plot_temp, COLOR_PRIMARY), (self.tds, self.plot_tds, COLOR_SECONDARY), (self.flex, self.plot_flex, COLOR_PRIMARY)]:
            plot.plot(self.steps, buf, pen=pg.mkPen(col, width=3), clear=True); plot.setXRange(max(0,i-MAX_POINTS), i)
        # xyz plots
        for plot, series in [(self.accel_plot, self.acc), (self.gyro_plot, self.gyro)]:
            for idx, ax in enumerate('XYZ'):
                plot.listDataItems()[idx].setData(self.steps, series[ax])
            plot.setXRange(max(0,i-MAX_POINTS), i)

        # cube
        self.cube.update_orientation(np.radians(d['GyroX']), np.radians(d['GyroY']), np.radians(d['GyroZ']))
