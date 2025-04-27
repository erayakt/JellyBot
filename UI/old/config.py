from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg

# Colors
COLOR_BG        = QColor(7, 25, 43)      # deep ocean
COLOR_PRIMARY   = QColor(0, 150, 200)    # ocean blue
COLOR_SECONDARY = QColor(0, 200, 150)    # sea green
COLOR_TEXT      = QColor(230, 230, 230)  # off‑white
COLOR_SHADOW    = QColor(0, 0, 0, 200)   # semi‑transparent black

# Fonts
FONT_HEADER = QFont("Arial Black", 24)
FONT_TITLE  = QFont("Arial", 17, QFont.Bold)
FONT_BODY   = QFont("Arial", 15)

# Styles
STYLE_BUTTON = f"""
QPushButton {{
    border: 2px solid {COLOR_PRIMARY.name()};
    border-radius: 10px;
    padding: 8px 20px;
    color: {COLOR_TEXT.name()};
    font: 15pt \"Arial\";
    background-color: rgba(0,150,200,110);
}}
QPushButton:hover {{
    background-color: rgba(0,180,240,160);
}}
"""

STYLE_FRAME = f"""
QFrame {{
    background-color: {COLOR_BG.darker(115).name()};
    border: 2px solid {COLOR_PRIMARY.darker(140).name()};
    border-radius: 12px;
}}
"""

# PyQtGraph defaults
pg.setConfigOption('background', COLOR_BG.name())
pg.setConfigOption('foreground', COLOR_TEXT.name())
pg.setConfigOption('antialias', True)