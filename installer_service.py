import win32serviceutil
import win32service
import win32event
import win32pipe
import win32file
import win32api
import win32con
import subprocess
import os
import json
import logging
import shlex
import sys
from typing import List, Dict, Optional

SERVICE_NAME = "PackageInstallerProService"
PIPE_NAME = r"\\.\pipe\PackageInstallerPipe"

# Robust path: Use EXE dir for bundled runs, script dir for dev
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(base_path, "config.json")

LOG_DIR = os.path.join(os.environ["ProgramData"], "PackageInstallerPro")
LOG_FILE = os.path.join(LOG_DIR, "install_service.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Basic log rotation: Truncate if > 10MB
if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 10 * 1024 * 1024:
    open(LOG_FILE, 'w').close()

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class PackageInstallerProService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = "Package Installer Pro Service"
    _svc_description_ = "Allows non-admin users to install curated apps through PackageInstallerPro."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.packages: List[Dict[str, str]] = []  # Initialize empty; load later to avoid startup delays
        self.repository_url: str = ""

    def load_packages(self) -> None:
        """Load repository_url from config.json and dynamically discover packages from the network path."""
        logging.info("Starting package load from repository.")
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Config must be a JSON object")
                if not isinstance(data.get("repository_url"), str):
                    raise ValueError("repository_url must be a string")
                self.repository_url = data["repository_url"]

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

            if not self.packages:
                logging.warning("No installers found in the repository path.")
            else:
                logging.info(f"Loaded {len(self.packages)} packages successfully.")

        except Exception as e:
            logging.error(f"Failed to load repository or packages: {e}")
            self.packages = []

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # Report running immediately to avoid SCM timeout (fixes Error 1053)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        logging.info("PackageInstallerProService has started successfully.")
        servicemanager.LogInfoMsg("PackageInstallerProService started.")
        # Load packages after reporting ready, to handle potential network delays gracefully
        self.load_packages()
        self.run()

    def run(self):
        while self.running:
            try:
                pipe = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                    1, 65536, 65536,
                    0, None
                )
                win32pipe.ConnectNamedPipe(pipe, None)
                _, data = win32file.ReadFile(pipe, 4096)
                command = data.decode("utf-8").strip()

                if command.startswith("INSTALL "):
                    response = self.handle_install(command)
                else:
                    response = "ERROR Invalid command"

                win32file.WriteFile(pipe, response.encode("utf-8"))
                win32file.CloseHandle(pipe)

            except Exception as e:
                logging.error(f"Service error: {e}")
                win32event.WaitForSingleObject(self.hWaitStop, 1000)

    def handle_install(self, command: str) -> str:
        """Handle installation with validation and logging."""
        try:
            parts = shlex.split(command[len("INSTALL "):])
            if not parts:
                return "ERROR No installer specified"
            installer_file = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # Validate against scanned packages
            pkg = next((p for p in self.packages if p["installer"] == installer_file), None)
            if not pkg:
                logging.warning(f"Unauthorized installer attempt: {installer_file}")
                return "ERROR Installer not authorized"

            installer_path = os.path.join(self.repository_url, installer_file)
            if not os.path.exists(installer_path):
                logging.error(f"Installer not found: {installer_path}")
                return "ERROR Installer not found in repository"

            try:
                user = win32api.GetUserNameEx(win32con.NameSamCompatible) or "Unknown"
                subprocess.run([installer_path] + args, check=True, timeout=1800)
                logging.info(f"Installed {installer_file} with args: {' '.join(args)} by user {user}")
                return "OK"
            except subprocess.TimeoutExpired:
                logging.error(f"Installation timeout for {installer_file}")
                return "ERROR Installation timed out"
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install {installer_file}: {e}")
                return f"ERROR Install failed: {e}"
            except Exception as e:
                logging.error(f"Unexpected install error for {installer_file}: {e}")
                return f"ERROR Unexpected error: {e}"
        except Exception as e:
            logging.error(f"Error processing install command: {e}")
            return f"ERROR Command processing failed: {e}"

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PackageInstallerProService)
