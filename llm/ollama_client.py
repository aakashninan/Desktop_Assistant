import subprocess
import json
import re
from config import MODEL, SYSTEM_PROMPT


def extract_json(text):
    """
    Extract first valid JSON object from messy LLM output.
    """
    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None


def query_llm(user_input):
    prompt = SYSTEM_PROMPT + "\nUser: " + user_input

    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )

    output = result.stdout.strip()

    # Clean ANSI escape codes
    output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output).strip()

    parsed = extract_json(output)

    if parsed and isinstance(parsed, dict):
        msg_type = parsed.get("type", "")

        # Answer → return plain text directly
        if msg_type == "answer":
            return parsed.get("content", "").strip()

        # Action → return dict so core.py can execute the tool
        if msg_type == "action":
            return parsed

    # Fallback: return raw text as-is
    return output