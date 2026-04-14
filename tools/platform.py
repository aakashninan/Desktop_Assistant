import os
import subprocess
import platform as py_platform
import datetime
import requests


def get_os():
    return py_platform.system().lower()


def open_file(path):
    try:
        # Expand ~ to the full home directory path (e.g., /Users/Aakash)
        # This allows you to say "open ~/Desktop/file.pdf"
        full_path = os.path.expanduser(path)

        os_type = get_os()

        if os_type == "darwin":  # macOS
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

        if os_type == "darwin":
            subprocess.run(["open", "-a", app_name])

        elif os_type == "windows":
            subprocess.run(f'start {app_name}', shell=True)

        elif os_type == "linux":
            subprocess.run([app_name])

        return f"Opened app: {app_name}"

    except Exception as e:
        return str(e)


def list_files(path="."):
    try:
        # Expand path here too so "list files in ~/Downloads" works
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
            timeout=5
        )
        return result.stdout if result.stdout else result.stderr

    except Exception as e:
        return str(e)


def get_time():
    """Returns the current system time."""
    return datetime.datetime.now().strftime("%I:%M %p")


def get_date():
    """Returns today's date."""
    return datetime.date.today().strftime("%B %d, %Y")


def get_weather(city="Kochi"):
    """Fetches current weather for a specific city. Defaults to Kochi."""
    try:
        # Using wttr.in for a quick, no-API-key weather check
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Weather service currently unavailable."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"