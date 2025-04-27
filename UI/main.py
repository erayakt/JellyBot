import sys
from PyQt5.QtWidgets import QApplication
from widgets.dashboard import OceanDashboard
from config import USE_MOCK_DATA

if not USE_MOCK_DATA:
    from utils.data import reader

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = OceanDashboard()
    win.showMaximized()
    exit_code = app.exec_()
    if not USE_MOCK_DATA:
        reader.stop()
    sys.exit(exit_code)
