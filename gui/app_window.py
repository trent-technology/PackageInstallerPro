# gui/app_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QScrollArea
import json
import os
import sys

def resource_path(relative_path):
    """Handle file paths inside PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PackageInstallerPro")
        self.setFixedSize(600, 400)
        self.load_config()
        self.build_ui()

    def load_config(self):
        try:
            with open(resource_path("config.json"), "r") as f:
                self.config = json.load(f)
        except Exception as e:
            self.config = {"apps": []}

    def build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Available Applications:"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(250)

        app_widget = QWidget()
        app_layout = QVBoxLayout()

        if not self.config.get("apps"):
            empty_label = QLabel("No applications available.")
            app_layout.addWidget(empty_label)

        app_widget.setLayout(app_layout)
        scroll.setWidget(app_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout.addWidget(scroll)
        layout.addWidget(self.progress_bar)
        central.setLayout(layout)
        self.setCentralWidget(central)
