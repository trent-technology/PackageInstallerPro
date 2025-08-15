from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox, QScrollArea
from installer.install_manager import download_and_install
import json, os

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Creative Cloud Clone")
        self.setFixedSize(600, 600)
        self.load_config()
        self.build_ui()

    def load_config(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)

    def build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        layout.addWidget(QLabel("Available Applications:"))
        scroll = QScrollArea()
        app_widget = QWidget()
        app_layout = QVBoxLayout()

        for app in self.config["apps"]:
            btn = QPushButton(f"Install {app['name']}")
            btn.clicked.connect(lambda checked, a=app: self.install_app(a))
            app_layout.addWidget(btn)

        app_widget.setLayout(app_layout)
        scroll.setWidget(app_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)
        layout.addWidget(self.progress_bar)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def install_app(self, app):
        installer_url = self.config["repository_url"] + app["filename"]
        self.progress_bar.setValue(0)
        download_and_install(installer_url, app["filename"], self.progress_bar, app["requires_admin"])
