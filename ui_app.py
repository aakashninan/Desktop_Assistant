import streamlit as st
from agent.core import run_agent

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
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
        border-right: 1px solid #1e293b;
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
# SIDEBAR (Control Center)
# -----------------------------
with st.sidebar:
    st.markdown("<h1 style='font-size: 22px;'>Desktop Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Active Terminal Session</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📡 System Info")
    st.caption("OS: macOS / Linux Core/Windows")
    st.caption("Status: Connected")
    
    if st.button("Reset Environment", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# -----------------------------
# MAIN INTERFACE
# -----------------------------
st.markdown("## Workspace")
st.markdown("<p style='color: #64748b;'>Control your local environment via natural language.</p>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat Area
chat_placeholder = st.container()

with chat_placeholder:
    for chat in st.session_state.chat_history:
        role_class = "user-bubble" if chat["role"] == "user" else "assistant-bubble"
        st.markdown(f"""
            <div style="display: flex; flex-direction: column;">
                <div class="chat-bubble {role_class}">
                    <b>{"You" if chat["role"] == "user" else "Assistant"}</b><br>
                    {chat["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

# -----------------------------
# ACTION BAR (Bottom Fixed-Style)
# -----------------------------
# We use st.chat_input as it's the only one that stays pinned and looks modern
if prompt := st.chat_input("Enter a system command (e.g., 'Open Chrome')"):
    
    # Update History
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Process
    with st.spinner("Processing system request..."):
        try:
            response = run_agent(prompt)
        except Exception as e:
            response = f"Critical Error: {str(e)}"
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()