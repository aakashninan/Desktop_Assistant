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
        app_name = app_name.lower()

        if os_type == "darwin":
            subprocess.run(["open", "-a", app_name])

        elif os_type == "windows":
            apps = {
                "chrome": "start chrome",
                "calculator": "start calc",
                "calc": "start calc",
                "word": "start winword",
                "notepad": "start notepad",
                "vs code": "start code",
                "vscode": "start code"
            }

            for key in apps:
                if key in app_name:
                    subprocess.run(apps[key], shell=True)
                    return f"Opened app: {key}"

            return f"App '{app_name}' not supported"

        elif os_type == "linux":
            subprocess.run([app_name])

        return f"Opened app: {app_name}"

    except Exception as e:
        return str(e)



def send_email(to_email, subject, body):
    try:
        sender = "your_email@gmail.com"
        password = "your_app_password"   # ⚠️ use app password

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return "Email sent successfully"

    except Exception as e:
        return str(e)
def close_app(app_name):
    """
    Kills a running application by name.
    Tries multiple name variations to handle cases like
    'microsoft outlook' -> 'Microsoft Outlook'.
    """
    try:
        os_type = get_os()

        # Build a list of name variations to try
        variations = [
            app_name,                          # as given: "microsoft outlook"
            app_name.title(),                  # title case: "Microsoft Outlook"
            app_name.capitalize(),             # first word cap: "Microsoft outlook"
            app_name.replace(" ", ""),         # no spaces: "microsoftoutlook"
            app_name.title().replace(" ", ""), # title + no spaces: "MicrosoftOutlook"
        ]

        if os_type == "darwin":
            # Try osascript first — most reliable for macOS GUI apps
            title_name = app_name.title()
            result = subprocess.run(
                ["osascript", "-e", f'tell application "{title_name}" to quit'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return f"Closed: {app_name}"

            # Fallback: try pkill with each variation
            for name in variations:
                result = subprocess.run(
                    ["pkill", "-ix", name],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return f"Closed: {app_name}"

            return f"Could not close '{app_name}'. Make sure it is running."

        elif os_type == "windows":
            for name in variations:
                exe = name if name.endswith(".exe") else name + ".exe"
                result = subprocess.run(
                    f'taskkill /F /IM "{exe}"',
                    shell=True, capture_output=True,
                    text=True, encoding="utf-8"
                )
                if result.returncode == 0:
                    return f"Closed: {app_name}"

            return f"Could not close '{app_name}'. Make sure it is running."

        elif os_type == "linux":
            for name in variations:
                result = subprocess.run(
                    ["pkill", "-i", name],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    return f"Closed: {app_name}"

            return f"Could not close '{app_name}'. Make sure it is running."

    except Exception as e:
        return str(e)


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