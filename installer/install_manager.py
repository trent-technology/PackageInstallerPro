import urllib.request
import subprocess
import os
from PyQt6.QtWidgets import QMessageBox

def download_and_install(url, filename, progress_bar, requires_admin):
    local_path = os.path.join("temp", filename)
    os.makedirs("temp", exist_ok=True)

    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(int(downloaded * 100 / total_size), 100)
            progress_bar.setValue(percent)

    try:
        urllib.request.urlretrieve(url, local_path, reporthook)
    except Exception as e:
        QMessageBox.critical(None, "Download Failed", str(e))
        return

    try:
        if requires_admin:
            # Requires elevation
            subprocess.run(['powershell', 'Start-Process', local_path, '-Verb', 'runAs'], check=True)
        else:
            subprocess.run([local_path], check=True)
    except Exception as e:
        QMessageBox.critical(None, "Installation Failed", str(e))
