import json
import os

FILE = "chat_history.json"

def load_history():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def save_chat(chat):
    history = load_history()

    found = False

    for i, existing in enumerate(history):
        if existing.get("id") == chat.get("id"):
            history[i] = chat   # ✅ update same chat
            found = True
            break

    if not found:
        history.append(chat)   # only new chat

    with open("chat_history.json", "w") as f:
        json.dump(history, f, indent=2)