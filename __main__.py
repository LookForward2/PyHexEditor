import sys
from PyQt5.QtWidgets import QApplication
from Window.QHexWindow import QHexWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('PyHexEditor')
    app.setOrganizationName('PyHexEditor')
    app.setStyle('Fusion')
    widget = QHexWindow(app.applicationName())
    sys.exit(app.exec_())
