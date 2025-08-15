import json
import os
import sys
import subprocess

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QMessageBox
)


def resource_path(relative_path):
    """Get absolute path to resource (for PyInstaller compatibility)."""
    if hasattr(sys, '_MEIPASS'):
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
            print(f"Failed to load config.json: {e}")

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
        else:
            for app in self.config.get("apps", []):
                btn = QPushButton(f"Install {app['name']}")
                btn.clicked.connect(lambda checked, a=app: self.install_app(a))
                app_layout.addWidget(btn)

        app_widget.setLayout(app_layout)
        scroll.setWidget(app_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout.addWidget(scroll)
        layout.addWidget(self.progress_bar)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def install_app(self, app):
        self.progress_bar.setValue(0)
        installer_path = os.path.join(self.config["repository_url"], app["installer"])

        try:
            subprocess.run([installer_path], check=True)
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", f"{app['name']} installed successfully.")
        except subprocess.CalledProcessError as e:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Error", f"Failed to install {app['name']}.\n\n{e}")
        except FileNotFoundError:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Error", f"Installer not found:\n{installer_path}")
