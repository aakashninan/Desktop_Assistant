import streamlit as st
from agent.core import run_agent

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Workspace",
    page_icon="💻",
    layout="wide"
)

# -----------------------------
# GLOBAL STYLE (clean + minimal)
# -----------------------------
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: "Inter", sans-serif;
    }

    .chat-container {
        max-width: 800px;
        margin: auto;
    }

    .msg-user {
        background: #f3f4f6;
        color: #111827;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 6px 0;
    }

    .msg-bot {
        background: #e5e7eb;
        color: #111827;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 6px 0;
    }

    .title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 10px;
    }

    .subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR (minimal)
# -----------------------------
with st.sidebar:
    st.markdown("### Workspace")
    st.write("Local system assistant")

    if st.button("Clear conversation"):
        st.session_state.chat = []

    st.markdown("---")
    st.write("Commands:")
    st.write("- open chrome")
    st.write("- list files")
    st.write("- open file.pdf")

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="title">Workspace</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Local command interface for your computer</div>', unsafe_allow_html=True)

# -----------------------------
# INIT CHAT
# -----------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# -----------------------------
# CHAT RENDER
# -----------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">You: {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">System: {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# INPUT
# -----------------------------
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "",
        placeholder="Type a command...",
        label_visibility="collapsed"
    )

with col2:
    send = st.button("Send")

# -----------------------------
# LOGIC
# -----------------------------
if send and user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    response = run_agent(user_input)

    st.session_state.chat.append({"role": "assistant", "content": response})

    st.rerun()