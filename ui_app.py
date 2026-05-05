import streamlit as st
import json
import uuid
import time
from memory.history import save_chat, load_history
from agent.core import run_agent
import sys
# -----------------------------
# INIT CHAT SESSION
# -----------------------------
if "current_chat" not in st.session_state:
    st.session_state.current_chat = {
        "id": str(uuid.uuid4()),
        "title": "New Chat",
        "messages": []
    }

# -----------------------------
# SAFE TEXT
# -----------------------------
def safe_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = text.replace("→", "->")
    return text.encode("utf-8", "ignore").decode("utf-8")

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Desktop Assistant",
    page_icon="⚡",
    layout="wide"
)


# -----------------------------
# PROFESSIONAL UI INJECTION
# -----------------------------
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Remove Streamlit Header/Footer */
    header {visibility: visible;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}

    /* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #0b1220;
}
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* FIX ALL TEXT COLORS IN SIDEBAR */
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Labels / captions */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #9ca3af !important;
}

/* Buttons (Recents + Reset) */
.stButton > button {
    width: 100%;
    background-color: transparent;
    color: #e5e7eb !important;
    border: none;
    text-align: left;
    padding: 10px 12px;
    border-radius: 8px;
}

/* Hover effect */
.stButton > button:hover {
    background-color: #1f2937;
    color: #ffffff !important;
}

/* Active click */
.stButton > button:focus {
    background-color: #374151;
    color: white !important;
}

/* Recents title */
.recents-title {
    color: #9ca3af !important;
    font-size: 14px;
    margin-bottom: 10px;
}
/* Remove ugly borders */
.stButton {
    margin-bottom: 5px;
}
    /* Main Container */
    .main-chat-wrapper {
        max-width: 900px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
    }

    /* Professional Message Bubbles */
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        max-width: 85%;
        line-height: 1.5;
        font-size: 14px;
        animation: fadeIn 0.3s ease-in;
    }

    .user-bubble {
        background-color: #ffffff;
        color: #1e293b;
        align-self: flex-end;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .assistant-bubble {
        background-color: #f8fafc;
        color: #334155;
        align-self: flex-start;
        border-left: 4px solid #3b82f6;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Command Tag Style */
    .cmd-tag {
        background: #1e293b;
        color: #94a3b8;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPER: Parse agent response
# -----------------------------
def parse_response(raw_response):
    """Extract clean text from JSON-wrapped agent responses."""
    if not isinstance(raw_response, str):
        return str(raw_response)
    
    stripped = raw_response.strip()
    
    # Try direct JSON parse
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            # Common keys the agent might use
            for key in ("content", "answer", "message", "text", "result", "output"):
                if key in parsed and isinstance(parsed[key], str):
                    return parsed[key].strip()
            # Fallback: join all string values
            values = [v for v in parsed.values() if isinstance(v, str)]
            if values:
                return " ".join(values).strip()
    except (json.JSONDecodeError, TypeError):
        pass

    # Handle cases where JSON is embedded inside extra text
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(stripped[start:end + 1])
            if isinstance(parsed, dict):
                for key in ("content", "answer", "message", "text", "result", "output"):
                    if key in parsed and isinstance(parsed[key], str):
                        return parsed[key].strip()
        except (json.JSONDecodeError, TypeError):
            pass

    # Return as-is if not JSON
    return raw_response

with st.sidebar:

    if st.button("➕ New Chat"):
        st.session_state.current_chat = {
            "id": str(uuid.uuid4()),
            "title": "New Chat",
            "messages": []
        }
        st.rerun()

    st.markdown("### 🕘 Recents")

    history = load_history()

    for i, chat in enumerate(history[::-1]):
        chat_id = chat.get("id", str(hash(chat["title"])))
        key = f"chat_{chat_id}_{i}"   # ✅ UNIQUE

        if st.button(chat["title"], key=key):
            st.session_state.current_chat = chat
            st.rerun()

    st.markdown("---")

    st.markdown("### 📡 System Info")
    st.caption("OS: macOS / Linux Core/Windows")
    st.caption("Status: Connected")

    if st.button("Reset Environment", use_container_width=True):
        st.session_state.current_chat["messages"] = []
        st.rerun()
# -----------------------------
# MAIN INTERFACE
# -----------------------------
st.markdown("## Workspace")
st.markdown("<p style='color: #64748b;'>Control your local environment via natural language.</p>", unsafe_allow_html=True)

# -----------------------------
# DISPLAY CHAT
# -----------------------------
chat_placeholder = st.container()

with chat_placeholder:
    for chat in st.session_state.current_chat["messages"]:
        role_class = "user-bubble" if chat["role"] == "user" else "assistant-bubble"
        st.markdown(f"""
            <div style="display: flex; flex-direction: column;">
                <div class="chat-bubble {role_class}">
                    <b>{"You" if chat["role"] == "user" else "Assistant"}</b><br>
                    {safe_text(chat["content"])}
                </div>
            </div>
        """, unsafe_allow_html=True)

# -----------------------------
# INPUT
# -----------------------------
if prompt := st.chat_input("Enter a system command..."):

    # Add user message
    st.session_state.current_chat["messages"].append({
        "role": "user",
        "content": prompt
    })

    # Process
    with st.spinner("Processing..."):
        try:
            raw = run_agent(prompt)
            response = raw if isinstance(raw, str) else str(raw)
        except Exception as e:
            response = f"Error: {str(e)}"

    # Add assistant response
    st.session_state.current_chat["messages"].append({
        "role": "assistant",
        "content": response
    })

    # Auto title (only first message)
    if st.session_state.current_chat["title"] == "New Chat":
        st.session_state.current_chat["title"] = prompt[:40]

    # Save full chat session
    save_chat(st.session_state.current_chat)

    st.rerun()