import os
import subprocess
import platform as py_platform
import datetime
import requests
import smtplib
from email.mime.text import MIMEText


def get_os():
    return py_platform.system().lower()


def open_file(path):
    try:
        full_path = os.path.expanduser(path)
        os_type = get_os()

        if os_type == "darwin":
            subprocess.run(["open", full_path])

        elif os_type == "windows":
            os.startfile(full_path)

        elif os_type == "linux":
            subprocess.run(["xdg-open", full_path])

        return f"Opened: {full_path}"

    except Exception as e:
        return str(e)


def open_app(app_name):
    try:
        os_type = get_os()
        app_name = app_name.strip()

        # -----------------------------
        # WINDOWS
        # -----------------------------
        if os_type == "windows":

            app_map = {
                "chrome": "chrome",
                "google chrome": "chrome",
                "calculator": "calc",
                "calc": "calc",
                "notepad": "notepad",
                "word": "winword",
                "excel": "excel",
                "powerpoint": "powerpnt",
                "vs code": "code",
                "vscode": "code",
                "edge": "msedge"
            }

            app_key = app_name.lower()

            # 🔹 Step 1: Known apps
            for key in app_map:
                if key in app_key:
                    subprocess.run(f'start "" "{app_map[key]}"', shell=True)
                    return f"Opened app: {key}"

            # 🔹 Step 2: Try opening anything (fallback)
            subprocess.run(f'start "" "{app_name}"', shell=True)
            return f"Trying to open: {app_name}"

        # -----------------------------
        # macOS
        # -----------------------------
        elif os_type == "darwin":
            try:
                subprocess.run(["open", "-a", app_name])
                return f"Opened app: {app_name}"
            except:
                subprocess.run(["open", app_name])
                return f"Trying to open: {app_name}"

        # -----------------------------
        # LINUX
        # -----------------------------
        elif os_type == "linux":
            try:
                subprocess.run([app_name])
                return f"Opened app: {app_name}"
            except:
                subprocess.run(["xdg-open", app_name])
                return f"Trying to open: {app_name}"

        else:
            return "Unsupported OS"

    except Exception as e:
        return f"Error: {str(e)}"

def close_app(app_name):
    try:
        import subprocess
        import platform

        os_type = platform.system().lower()
        app_name = app_name.lower()

        # -----------------------------
        # WINDOWS
        # -----------------------------
        if os_type == "windows":

            app_map = {
                "chrome": "chrome.exe",
                "calculator": "CalculatorApp.exe",
                "calc": "CalculatorApp.exe",
                "notepad": "notepad.exe",
                "word": "WINWORD.EXE",
                "excel": "EXCEL.EXE",
                "powerpoint": "POWERPNT.EXE",
                "vs code": "Code.exe",
                "vscode": "Code.exe",
                "edge": "msedge.exe"
            }

            for key in app_map:
                if key in app_name:
                    exe = app_map[key]

                    result = subprocess.run(
                        f'taskkill /F /IM "{exe}"',
                        shell=True,
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        return f"Closed app: {key}"
                    else:
                        return f"App '{key}' is not running or cannot be closed"

            return f"App '{app_name}' not recognized"

        # -----------------------------
        # macOS
        # -----------------------------
        elif os_type == "darwin":

            result = subprocess.run(
                ["osascript", "-e", f'tell application "{app_name}" to quit'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return f"Closed app: {app_name}"
            else:
                return f"Could not close '{app_name}'"

        # -----------------------------
        # LINUX
        # -----------------------------
        elif os_type == "linux":

            result = subprocess.run(
                ["pkill", "-f", app_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return f"Closed app: {app_name}"
            else:
                return f"App '{app_name}' is not running"

        else:
            return "Unsupported OS"

    except Exception as e:
        return f"Error closing app: {str(e)}"

def list_files(path="."):
    try:
        full_path = os.path.expanduser(path)
        return os.listdir(full_path)
    except Exception as e:
        return str(e)


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8"
        )
        return result.stdout if result.stdout else result.stderr

    except Exception as e:
        return str(e)


def get_time():
    return datetime.datetime.now().strftime("%I:%M %p")


def get_date():
    return datetime.date.today().strftime("%B %d, %Y")


def get_weather(city="Kochi"):
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Weather service currently unavailable."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"