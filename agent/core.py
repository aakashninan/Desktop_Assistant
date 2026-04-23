import json
import re
import subprocess
from llm.ollama_client import query_llm
from tools.file_tools import read_file, write_file
from tools.platform import open_file, open_app, close_app, list_files, run_command, get_time, get_date, get_weather
from memory.knowledge import add_memory
from config import MODEL, CONTENT_MODEL, CONTENT_GENERATION_PROMPT


# -----------------------------
# CONTENT GENERATION KEYWORDS
# -----------------------------
GENERATE_TRIGGERS = [
    "write a", "write an", "write me",
    "generate a", "generate an", "generate me",
    "create a", "create an",
    "draft a", "draft an",
    "compose a", "compose an",
    "make a poem", "make a story", "make an essay",
    "give me a poem", "give me a story", "give me an essay",
]

CONTENT_TYPES = [
    "blog", "blog post", "article", "essay", "story",
    "poem", "email", "letter", "report", "summary",
    "cover letter", "resume", "bio", "description",
    "caption", "script", "speech", "paragraph",
    "product description", "tweet", "post", "message",
]

# -----------------------------
# CLOSE APP TRIGGERS
# -----------------------------
CLOSE_TRIGGERS = ["close ", "quit ", "kill ", "exit ", "stop ", "shut down "]


# -----------------------------
# DETECT CONTENT GENERATION
# -----------------------------
def is_content_request(user_input):
    text = user_input.lower().strip()

    for trigger in GENERATE_TRIGGERS:
        if text.startswith(trigger):
            return True

    for content_type in CONTENT_TYPES:
        if content_type in text:
            for trigger in ["write", "generate", "create", "draft", "compose", "make", "give me"]:
                if trigger in text:
                    return True

    return False


# -----------------------------
# DETECT CLOSE APP REQUEST
# -----------------------------
def is_close_request(user_input):
    """Returns the app name if it's a close request, else None."""
    text = user_input.lower().strip()
    for trigger in CLOSE_TRIGGERS:
        if text.startswith(trigger):
            return text.replace(trigger, "", 1).strip()
    return None


# -----------------------------
# GENERATIVE CONTENT ENGINE
# -----------------------------
def generate_content(user_input):
    """
    Uses CONTENT_MODEL (llama3) for clean, typo-free content generation.
    Completely separate from the JSON-based tool/answer pipeline.
    """
    prompt = CONTENT_GENERATION_PROMPT + "\n" + user_input

    result = subprocess.run(
        ["ollama", "run", CONTENT_MODEL],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    output = result.stdout.strip()
    output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output).strip()

    return output if output else "Sorry, I couldn't generate content for that request."


# -----------------------------
# TOOL EXECUTOR
# -----------------------------
def execute_tool(tool, args):
    if tool == "get_time":
        return get_time()
    elif tool == "get_date":
        return get_date()
    elif tool == "get_weather":
        return get_weather(args.get("city", "Kochi"))
    elif tool == "open_file":
        return open_file(args.get("path"))
    elif tool == "open_anything":
        name = args.get("name")
        if name and "." in name:
            return open_file(name)
        return open_app(name)
    elif tool == "open_app":
        return open_app(args.get("name"))
    elif tool == "close_app":
        return close_app(args.get("name"))
    elif tool == "list_files":
        return list_files(args.get("path", "."))
    elif tool == "run_command":
        return run_command(args.get("command"))

    return "Unknown tool"


# -----------------------------
# FALLBACK INTENT PARSER
# -----------------------------
def simple_intent_parser(user_input):
    text = user_input.lower().strip()

    if "time" in text:
        return {"type": "action", "tool": "get_time", "args": {}}

    if "date" in text or "today" in text:
        return {"type": "action", "tool": "get_date", "args": {}}

    if "weather" in text:
        city = "Kochi"
        if "in " in text:
            city = text.split("in ")[-1].strip()
        return {"type": "action", "tool": "get_weather", "args": {"city": city}}

    if text.startswith("open "):
        name = text.replace("open", "", 1).strip()
        return {"type": "action", "tool": "open_anything", "args": {"name": name}}

    # Close app detection
    app_name = is_close_request(user_input)
    if app_name:
        return {"type": "action", "tool": "close_app", "args": {"name": app_name}}

    return None


# -----------------------------
# RESPONSE EXTRACTOR
# -----------------------------
def extract_clean_response(data):
    """
    Takes whatever query_llm returns (dict or raw string)
    and always returns a plain string or an action dict.
    """
    if isinstance(data, dict):
        msg_type = data.get("type", "")

        if msg_type == "answer":
            return data.get("content", "").strip()

        if msg_type == "action":
            return data

        for key in ("content", "text", "message", "answer", "result", "output"):
            if key in data and isinstance(data[key], str):
                return data[key].strip()

        return str(data)

    if isinstance(data, str):
        data = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', data).strip()

        match = re.search(r'\{.*\}', data, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return extract_clean_response(parsed)
            except (json.JSONDecodeError, ValueError):
                pass

        return data

    return "I'm sorry, I couldn't process that request."


# -----------------------------
# MAIN AGENT LOOP
# -----------------------------
def run_agent(user_input):
    # STEP 1: Content generation (uses llama3 — fast and clean)
    if is_content_request(user_input):
        return generate_content(user_input)

    # STEP 2: Local intent parser (time, date, weather, open, close)
    local_intent = simple_intent_parser(user_input)

    if local_intent:
        processed = local_intent
    else:
        # STEP 3: Ask the LLM (uses mistral for tool routing + Q&A)
        raw_response = query_llm(user_input)
        processed = extract_clean_response(raw_response)

    # STEP 4: Execute tool or return answer
    if isinstance(processed, str):
        return processed

    if isinstance(processed, dict):
        if processed.get("type") == "action":
            tool = processed.get("tool")
            args = processed.get("args", {})
            result = execute_tool(tool, args)
            add_memory({"input": user_input, "tool": tool, "args": args, "result": result})
            return f"[RESULT]: {result}"

        if processed.get("type") == "answer":
            return processed.get("content", "").strip()

    return "I'm sorry, I couldn't process that request."