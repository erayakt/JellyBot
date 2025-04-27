import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget, QGroupBox, QPushButton, QLabel, QFrame, QStatusBar, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt, QSize

import pyqtgraph as pg
from config import *
from utils.data import generate_data
from utils.ui_helpers import add_shadow
from widgets.ocean_cube import OceanCubeCanvas
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from utils.life_detector import LifeDetector
from PyQt5.QtWidgets import QProgressBar
import os


from config import USE_MOCK_DATA
if not USE_MOCK_DATA:
    from utils.data import reader


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
        self.detector = LifeDetector()
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
        graph_tabs.addTab(self._build_photos_tab(), "Photos")
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
    from config import GRAPH_Y_LIMITS

    @staticmethod
    def _make_line_plot(title):
        p = pg.PlotWidget(title=title)
        p.setTitle(title, color=COLOR_TEXT.name(), size="12pt")
        p.getAxis('bottom').setPen(COLOR_TEXT.name())
        p.getAxis('left').setPen(COLOR_TEXT.name())

        if "Temp" in title:
            p.setYRange(*GRAPH_Y_LIMITS["Temperature_C"])
        elif "TDS" in title:
            p.setYRange(*GRAPH_Y_LIMITS["TDS_ppm"])
        elif "Flex" in title:
            p.setYRange(*GRAPH_Y_LIMITS["Flex Voltage"])

        return p

    @staticmethod
    def _make_xyz_plot(title):
        p = pg.PlotWidget(title=title)
        p.setTitle(title, color=COLOR_TEXT.name(), size="12pt")
        p.getAxis('bottom').setPen(COLOR_TEXT.name())
        p.getAxis('left').setPen(COLOR_TEXT.name())

        if "Accel" in title:
            p.setYRange(*GRAPH_Y_LIMITS["Accel"])
        elif "Gyro" in title:
            p.setYRange(*GRAPH_Y_LIMITS["Gyro"])

        for clr in ('r', 'g', 'b'):
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
        global running, mission_time, data_log
        running, mission_time = True, 0
        self.msg_lbl.setText("Running")

        # CLEAR EVERYTHING
        data_log.clear()

        self.steps.clear()
        self.temp.clear()
        self.tds.clear()
        self.flex.clear()
        for ax in 'XYZ':
            self.acc[ax].clear()
            self.gyro[ax].clear()

        # Clear plots immediately
        for plot in (self.plot_temp, self.plot_tds, self.plot_flex):
            plot.clear()
        for plot in (self.accel_plot, self.gyro_plot):
            for item in plot.listDataItems():
                item.clear()

        self.detector = LifeDetector()

    def _stop(self):
        global running
        running = False; self.msg_lbl.setText("Paused")

    def _save(self):
        pd.DataFrame(data_log).to_csv("data.csv", index=False); self.msg_lbl.setText("Data saved to data.csv")

    # ------------------------------------------------------------------
    def _tick(self):
        global mission_time
        if not running:
            return

        mission_time += 0.4
        m, s = divmod(int(mission_time), 60)
        self.time_lbl.setText(f"{m:02d}:{s:02d}")

        d = generate_data()
        if d is None:
            return  # if serial not ready yet, skip frame

        # Prepare ML sample
        sample = [
            d["Temperature_C"],
            d["TDS_ppm"],
            d["AccelX"],
            d["AccelY"],
            d["AccelZ"],
            d["GyroX"],
            d["GyroY"],
            d["GyroZ"],
        ]

        self.detector.add_sample(sample)
        interest_score = self.detector.predict_interest(sample)

        # Update message bar
        self.msg_lbl.setText(f"🌟 Interest Score: {interest_score:.2f}")

        # Optional: Color feedback based on score
        if interest_score > 0.7:
            self.msg_lbl.setStyleSheet("color: red; font-weight: bold;")
        elif interest_score > 0.4:
            self.msg_lbl.setStyleSheet("color: orange;")
        else:
            self.msg_lbl.setStyleSheet(f"color:{COLOR_TEXT.name()};")


        # Update interest bar
        self.interest_bar.setValue(int(interest_score * 100))

        # Dynamic color
        if interest_score > 0.7:
            color = "red"
        elif interest_score > 0.4:
            color = "orange"
        else:
            color = "green"

        self.interest_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #aaa;
                border-radius: 8px;
                background-color: #222;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)



        data_log.append(d)
        i = len(data_log)
        self.steps.append(i)
        self.temp.append(d['Temperature_C'])
        self.tds.append(d['TDS_ppm'])
        self.flex.append(d['Flex Voltage'])
        for ax in 'XYZ':
            self.acc[ax].append(d[f'Accel{ax}'])
            self.gyro[ax].append(d[f'Gyro{ax}'])

        if i > MAX_POINTS:
            for seq in (self.steps, self.temp, self.tds, self.flex):
                seq.pop(0)
            for dic in (self.acc, self.gyro):
                for ax in 'XYZ':
                    dic[ax].pop(0)

        # update UI
        self.temp_lbl.setText(f"🌡 Temp: {d['Temperature_C']:.2f} °C")
        self.tds_lbl.setText(f"💧 TDS: {d['TDS_ppm']:.0f} ppm")
        self.flex_lbl.setText(f"📏 Flex: {d['Flex Voltage']:.2f} V")

        # env plots
        for buf, plot, col in [(self.temp, self.plot_temp, COLOR_PRIMARY),
                            (self.tds, self.plot_tds, COLOR_SECONDARY),
                            (self.flex, self.plot_flex, COLOR_PRIMARY)]:
            plot.plot(self.steps, buf, pen=pg.mkPen(col, width=3), clear=True)
            plot.setXRange(max(0, i - MAX_POINTS), i)

        # motion plots
        for plot, series in [(self.accel_plot, self.acc), (self.gyro_plot, self.gyro)]:
            for idx, ax in enumerate('XYZ'):
                plot.listDataItems()[idx].setData(self.steps, series[ax])
            plot.setXRange(max(0, i - MAX_POINTS), i)

        # update cube
        self.cube.update_orientation(
            np.radians(d['GyroX']),
            np.radians(d['GyroY']),
            np.radians(d['GyroZ'])
        )

    def _build_status_bar(self):
        bar = QStatusBar()
        self.time_lbl = QLabel("00:00")
        self.msg_lbl = QLabel("Ready")
        
        for w in (self.time_lbl, self.msg_lbl):
            w.setFont(FONT_BODY)
            w.setStyleSheet(f"color:{COLOR_TEXT.name()}")

        self.interest_bar = QProgressBar()
        self.interest_bar.setMaximumWidth(300)
        self.interest_bar.setMinimumWidth(200)
        self.interest_bar.setRange(0, 100)
        self.interest_bar.setValue(0)
        self.interest_bar.setFormat("")  # Hide percentage text
        self.interest_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #aaa;
                border-radius: 8px;
                background-color: #222;
            }
            QProgressBar::chunk {
                background-color: green;
                border-radius: 6px;
            }
        """)

        bar.addPermanentWidget(self.time_lbl)
        bar.addWidget(self.msg_lbl)
        bar.addPermanentWidget(self.interest_bar)

        return bar

   

    def _build_photos_tab(self):
        w = QWidget()
        v = QVBoxLayout(w)

        # Button Row
        button_row = QHBoxLayout()

        self.capture_btn = QPushButton("📸 Capture Photo")
        self.capture_btn.setFont(FONT_BODY)
        self.capture_btn.setStyleSheet(STYLE_BUTTON)
        self.capture_btn.clicked.connect(self._capture_photo)

        self.left_btn = QPushButton("⬅️ Rotate Left")
        self.left_btn.setFont(FONT_BODY)
        self.left_btn.setStyleSheet(STYLE_BUTTON)
        self.left_btn.clicked.connect(self._rotate_left)

        self.right_btn = QPushButton("➡️ Rotate Right")
        self.right_btn.setFont(FONT_BODY)
        self.right_btn.setStyleSheet(STYLE_BUTTON)
        self.right_btn.clicked.connect(self._rotate_right)

        for btn in (self.capture_btn, self.left_btn, self.right_btn):
            button_row.addWidget(btn)

        v.addLayout(button_row)

        # Gallery
        self.gallery = QListWidget()
        self.gallery.setViewMode(QListWidget.IconMode)
        self.gallery.setIconSize(QSize(150, 150))
        self.gallery.setResizeMode(QListWidget.Adjust)
        self.gallery.setSpacing(10)
        self.gallery.setSelectionMode(QListWidget.SingleSelection)
        self.gallery.setSelectionBehavior(QListWidget.SelectItems)

        self.gallery.itemDoubleClicked.connect(self._show_photo_popup)

        v.addWidget(self.gallery)

        return w

   
    def _capture_photo(self):
        if USE_MOCK_DATA:
            pixmap = QPixmap(150, 150)
            pixmap.fill(Qt.gray)
            item = QListWidgetItem(QIcon(pixmap), f"Mock Photo {self.gallery.count()+1}")
            self.gallery.addItem(item)
        else:
            print("[Dashboard] Sending SNAP command")
            reader.send_command("SNAP")
            reader.on_photo_received = self._process_photo


    def _rotate_left(self):
        if not USE_MOCK_DATA:
            reader.send_command("LEFT")
        print("Rotate Servo Left")

    def _rotate_right(self):
        if not USE_MOCK_DATA:
            reader.send_command("RIGHT")
        print("Rotate Servo Right")

    def _process_photo(self, photo_bytes):
        print(f"[Dashboard] Received photo, size: {len(photo_bytes)} bytes")

        try:
            os.makedirs("captured_photos", exist_ok=True)
            photo_path = f"captured_photos/photo_{self.gallery.count()+1}.jpg"
            with open(photo_path, "wb") as f:
                f.write(photo_bytes)

            pixmap = QPixmap(photo_path)
            icon = QIcon(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            item = QListWidgetItem(icon, f"Photo {self.gallery.count()+1}")
            self.gallery.addItem(item)

            print(f"[Dashboard] Photo saved and displayed: {photo_path}")

        except Exception as e:
            print("Error processing photo:", e)


   

    def _show_photo_popup(self, item):
        try:
            # Find the image path based on item index
            index = self.gallery.row(item)
            photo_path = f"captured_photos/photo_{index+1}.jpg"

            # Create popup window
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Photo {index+1}")
            dialog.resize(600, 600)

            layout = QVBoxLayout(dialog)
            label = QLabel()
            pixmap = QPixmap(photo_path)

            # Scale pixmap nicely
            label.setPixmap(pixmap.scaled(dialog.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setAlignment(Qt.AlignCenter)

            layout.addWidget(label)

            dialog.exec_()

        except Exception as e:
            print("Error opening photo:", e)