from PyQt5.QtWidgets import QApplication
import sys
from app_window import PackageInstallerPro

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackageInstallerPro()
    window.show()
    sys.exit(app.exec_())
