import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox
)
from install_manager import send_install_command

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class PackageInstallerPro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PackageInstallerPro")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.label = QLabel("Select a program to install:")
        self.program_list = QListWidget()
        self.install_button = QPushButton("Install Selected Program")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.program_list)
        self.layout.addWidget(self.install_button)

        self.setLayout(self.layout)
        self.install_button.clicked.connect(self.install_selected_program)

        self.load_config()

    def load_config(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                self.packages = data["packages"]
                for pkg in self.packages:
                    self.program_list.addItem(pkg["name"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config.json:\n{e}")

    def install_selected_program(self):
        selected = self.program_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No selection", "Please select a program to install.")
            return

        pkg = next((p for p in self.packages if p["name"] == selected.text()), None)
        if not pkg:
            QMessageBox.critical(self, "Error", "Program not found in config.")
            return

        success, message = send_install_command(pkg["installer"], pkg["silent_args"])

        if success:
            QMessageBox.information(self, "Success", f"{pkg['name']} installed successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Install failed:\n{message}")
