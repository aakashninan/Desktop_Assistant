import subprocess
import os


def open_anything(name):
    """
    Opens apps OR files dynamically (Mac only).
    """

    try:
        # 1. Try opening directly (works for apps like Safari)
        subprocess.run(["open", "-a", name], check=True)
        return f"Opened app: {name}"
    except:
        pass

    try:
        # 2. Try opening as file/path
        subprocess.run(["open", name], check=True)
        return f"Opened file: {name}"
    except:
        pass

    try:
        # 3. Search system for file/app using spotlight
        result = subprocess.run(
            ["mdfind", name],
            capture_output=True,
            text=True
        )

        paths = result.stdout.strip().split("\n")

        if paths and paths[0]:
            subprocess.run(["open", paths[0]])
            return f"Opened: {paths[0]}"

    except Exception as e:
        return str(e)

    return "Could not find anything to open"


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)