import win32serviceutil
import win32service
import win32event
import servicemanager
import win32pipe
import win32file
import subprocess
import os
import logging

SERVICE_NAME = "PackageInstallerProService"
PIPE_NAME = r"\\.\pipe\PackageInstallerPipe"
ALLOWED_INSTALLER_DIR = r"\\YourNetworkShare\Installers"  # 🔁 Replace this

LOG_FILE = os.path.join(os.environ["ProgramData"], "PackageInstallerPro", "install_service.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PackageInstallerProService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = "Package Installer Pro Service"
    _svc_description_ = "Allows non-admin users to request software installs approved by IT."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg(f"{SERVICE_NAME} started.")
        self.run()

    def run(self):
        while self.running:
            try:
                logging.info("Waiting for install request...")
                pipe = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                    1, 65536, 65536,
                    0, None
                )

                win32pipe.ConnectNamedPipe(pipe, None)
                result, data = win32file.ReadFile(pipe, 4096)
                command = data.decode("utf-8").strip()
                logging.info(f"Received command: {command}")

                response = self.handle_command(command)

                win32file.WriteFile(pipe, response.encode("utf-8"))
                win32file.CloseHandle(pipe)

            except Exception as e:
                logging.error(f"Service error: {e}")

    def handle_command(self, command):
        if not command.startswith("INSTALL "):
            return "ERROR Invalid command"

        parts = command[len("INSTALL "):].split()
        if not parts:
            return "ERROR No installer specified"

        installer_file = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        installer_path = os.path.join(ALLOWED_INSTALLER_DIR, installer_file)

        if not installer_path.startswith(ALLOWED_INSTALLER_DIR):
            return "ERROR Installer path not allowed"

        if not os.path.exists(installer_path):
            return "ERROR Installer file not found"

        try:
            subprocess.run([installer_path] + args, check=True)
            logging.info(f"Successfully installed: {installer_file}")
            return "OK"
        except subprocess.CalledProcessError as e:
            logging.error(f"Install failed for {installer_file}: {e}")
            return f"ERROR Install failed: {e}"


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PackageInstallerProService)
