import os
import json
import shlex
import sys
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox, QProgressDialog, QApplication
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from install_manager import send_install_command

# Robust path: Use EXE dir for bundled runs, script dir for dev
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(base_path, "config.json")

class InstallWorker(QThread):
    result = pyqtSignal(bool, str)
    
    def __init__(self, installer: str, args: str):
        super().__init__()
        self.installer = installer
        self.args = args
    
    def run(self):
        success, msg = send_install_command(self.installer, self.args)
        self.result.emit(success, msg)

class PackageInstallerPro(QWidget):
    def __init__(self):
        super().__init__()
        self.app_version = "Unknown"
        self.repository_url = ""
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

        self.packages: List[Dict[str, str]] = []
        self.load_packages()

    def load_packages(self) -> None:
        """Load repository_url from config.json and dynamically discover packages from the network path."""
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Config must be a JSON object")
                required_keys = {"app_version", "repository_url"}
                if not required_keys.issubset(data.keys()):
                    raise ValueError(f"Missing required keys in config: {required_keys - set(data.keys())}")
                if not isinstance(data["app_version"], str):
                    raise ValueError("app_version must be a string")
                if not isinstance(data["repository_url"], str):
                    raise ValueError("repository_url must be a string")
                
                self.app_version = data["app_version"]
                self.repository_url = data["repository_url"]
                self.setWindowTitle(f"PackageInstallerPro v{self.app_version}")

            # Dynamically scan the repository for installers
            if not os.path.exists(self.repository_url):
                raise OSError(f"Repository path not found: {self.repository_url}")

            files = os.listdir(self.repository_url)
            self.packages = []
            for file in files:
                if file.lower().endswith(('.exe', '.msi')):
                    base_name, ext = os.path.splitext(file)
                    pkg = {
                        "name": base_name,
                        "installer": file,
                        "silent_args": "/S" if ext.lower() == '.exe' else "/quiet /norestart",
                        "description": "Auto-detected installer",
                        "version": "N/A"
                    }
                    # Check for optional metadata JSON
                    metadata_path = os.path.join(self.repository_url, f"{base_name}.json")
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as mf:
                            metadata = json.load(mf)
                            if isinstance(metadata, dict):
                                pkg.update({k: metadata.get(k, pkg[k]) for k in ["silent_args", "description", "version"]})
                    self.packages.append(pkg)
                    item_text = f"{pkg['name']} (v{pkg.get('version', 'N/A')}) - {pkg.get('description', 'No description')}"
                    self.program_list.addItem(item_text)

            if not self.packages:
                QMessageBox.warning(self, "No Packages", "No installers found in the repository path.")

        except (json.JSONDecodeError, ValueError, OSError) as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load repository or packages:\n{str(e)}")
            self.packages = []

    def install_selected_program(self) -> None:
        """Handle installation of the selected program with progress feedback."""
        selected_item: Optional[QListWidgetItem] = self.program_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a program to install.")
            return

        selected_text = selected_item.text().split(" (v")[0]
        pkg: Optional[Dict[str, str]] = next((p for p in self.packages if p["name"] == selected_text), None)
        if not pkg:
            QMessageBox.critical(self, "Error", "Selected program not found.")
            return

        progress = QProgressDialog(f"Installing {pkg['name']}...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.show()
        QApplication.processEvents()

        self.worker = InstallWorker(pkg["installer"], pkg["silent_args"])
        self.worker.result.connect(lambda success, msg: self.handle_install_result(success, msg, pkg["name"], progress))
        self.worker.start()

    def handle_install_result(self, success: bool, message: str, pkg_name: str, progress: QProgressDialog) -> None:
        progress.cancel()
        if success:
            QMessageBox.information(self, "Success", f"{pkg_name} installed successfully.")
        else:
            QMessageBox.critical(self, "Install Failed", f"Failed to install {pkg_name}:\n{message}")
