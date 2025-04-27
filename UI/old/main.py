import sys
from PyQt5.QtWidgets import QApplication
from dashboard import OceanDashboard

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = OceanDashboard()
    win.showMaximized()
    sys.exit(app.exec_())