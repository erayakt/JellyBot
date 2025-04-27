from PyQt5.QtGui import QFont, QColor

# Colors
COLOR_BG        = QColor(7, 25, 43)      
COLOR_PRIMARY   = QColor(0, 150, 200)    
COLOR_SECONDARY = QColor(0, 200, 150)    
COLOR_TEXT      = QColor(230, 230, 230)  
COLOR_SHADOW    = QColor(0, 0, 0, 200)   

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
    font: 15pt "Arial";
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

GRAPH_Y_LIMITS = {
    "Temperature_C": (0, 40),    # 0°C to 10°C
    "TDS_ppm": (0, 500),          # 0 to 500 ppm
    "Flex Voltage": (0, 4.0),     # 0V to 3.3V
    "Accel": (-5, 5),             # -2g to 2g
    "Gyro": (-200, 200),          # -200°/s to 200°/s
}

USE_MOCK_DATA = True

# If not using mock, configure serial connection
SERIAL_PORT = "COM3" 
SERIAL_BAUDRATE = 115200

