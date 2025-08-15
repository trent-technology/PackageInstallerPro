import win32file

PIPE_NAME = r"\\.\pipe\PackageInstallerPipe"

def send_install_command(installer_filename, silent_args):
    try:
        pipe = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

        command = f"INSTALL {installer_filename} {silent_args}"
        win32file.WriteFile(pipe, command.encode('utf-8'))

        result, response = win32file.ReadFile(pipe, 4096)
        win32file.CloseHandle(pipe)

        output = response.decode('utf-8').strip()

        if output == "OK":
            return True, "Success"
        else:
            return False, output

    except Exception as e:
        return False, str(e)
