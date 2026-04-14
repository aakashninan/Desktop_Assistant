import json
import re
from llm.ollama_client import query_llm
from tools.file_tools import read_file, write_file
from tools.platform import open_file, open_app, list_files, run_command, get_time, get_date, get_weather
from memory.knowledge import add_memory


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
    elif tool == "list_files":
        return list_files(args.get("path", "."))
    elif tool == "run_command":
        return run_command(args.get("command"))
    
    return "Unknown tool"

# -----------------------------
# FALLBACK INTENT PARSER
# -----------------------------
def simple_intent_parser(user_input):
    """
    Checks for keywords locally before asking the LLM. 
    This prevents the LLM from 'talking' about tools instead of using them.
    """
    text = user_input.lower().strip()
    
    # 1. TIME check
    if "time" in text:
        return {"type": "action", "tool": "get_time", "args": {}}
    
    # 2. DATE check
    if "date" in text or "today" in text:
        return {"type": "action", "tool": "get_date", "args": {}}
    
    # 3. WEATHER check
    if "weather" in text:
        city = "Kochi"
        if "in " in text:
            city = text.split("in ")[-1].strip()
        return {"type": "action", "tool": "get_weather", "args": {"city": city}}
    
    # 4. OPEN check
    if text.startswith("open "):
        name = text.replace("open", "", 1).strip()
        return {"type": "action", "tool": "open_anything", "args": {"name": name}}
    
    return None

# -----------------------------
# RECURSIVE JSON PARSER
# -----------------------------
def deep_parse_response(data):
    """
    Keeps extracting 'content' if the LLM nests JSON inside strings.
    Also strips ANSI escape codes like [K or [1D.
    """
    if isinstance(data, str):
        # Clean ANSI codes
        data = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', data)
        
        try:
            json_match = re.search(r'\{.*\}', data, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return data.strip()
        except:
            return data.strip()

    if isinstance(data, dict):
        msg_type = data.get("type")
        content = data.get("content")

        if msg_type == "answer":
            # If the content is itself a JSON string, drill down
            if isinstance(content, str) and "{" in content:
                return deep_parse_response(content)
            return content
        
        return data 

    return data

# -----------------------------
# MAIN AGENT LOOP
# -----------------------------
def run_agent(user_input):
    # STEP 1: Check Local Intent Parser FIRST
    # This makes 'time', 'date', etc., work instantly and cleanly.
    local_intent = simple_intent_parser(user_input)
    
    if local_intent:
        processed = local_intent
    else:
        # STEP 2: Ask the LLM if it's not a local command
        raw_response = query_llm(user_input)
        processed = deep_parse_response(raw_response)

    # STEP 3: Execute and Return
    if isinstance(processed, str):
        return processed

    if isinstance(processed, dict):
        # Handle Tool/Action
        if processed.get("type") == "action":
            tool = processed.get("tool")
            args = processed.get("args", {})
            result = execute_tool(tool, args)
            
            add_memory({"input": user_input, "tool": tool, "args": args, "result": result})
            return f"[RESULT]: {result}"
        
        # Handle Human Answer
        if processed.get("type") == "answer":
            return processed.get("content")

    return "I'm sorry, I couldn't process that request."