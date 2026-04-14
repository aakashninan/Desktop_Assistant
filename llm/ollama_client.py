import subprocess
import json
import re
from config import MODEL, SYSTEM_PROMPT


def extract_json(text):
    """
    Extract first valid JSON object from messy LLM output
    """
    try:
        return json.loads(text)
    except:
        pass

    # try regex fix (VERY IMPORTANT)
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

    parsed = extract_json(output)

    if parsed:
        return parsed

    return {
        "type": "answer",
        "content": output
    }