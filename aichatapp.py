"""
PHANI AI - Gemini Powered Real-time AI Assistant
Built with Streamlit, Google Gemini LLM API, Python NLP & Context Manager.
"""

import os
import time
import streamlit as st
import pandas as pd

# Import NLP Engine
from nlp_engine import ChatbotEngine

# Page Config
st.set_page_config(
    page_title="Phani AI - Real Gemini Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Cobalt & Cyan Aesthetic
CUSTOM_CSS = """
<style>
    /* Dark Theme Customization */
    .stApp {
        background: radial-gradient(circle at top left, #1e1b4b 0%, #090d16 50%, #04060a 100%);
        color: #f8fafc;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85);
        border-right: 1px solid rgba(56, 189, 248, 0.18);
        backdrop-filter: blur(16px);
    }
    
    /* Header Badge */
    .brand-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(30, 41, 59, 0.8);
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid rgba(6, 182, 212, 0.3);
        margin-bottom: 20px;
    }
    
    .project-num {
        background: linear-gradient(135deg, #06b6d4, #3b82f6);
        color: #ffffff;
        font-weight: 800;
        font-size: 1.3rem;
        padding: 4px 10px;
        border-radius: 6px;
    }
    
    .brand-title {
        font-weight: 800;
        font-size: 1.25rem;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #ffffff, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Live HUD Cards */
    .hud-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    .hud-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .intent-val {
        font-family: monospace;
        font-size: 1rem;
        font-weight: 700;
        color: #22d3ee;
    }

    .entity-chip {
        display: inline-block;
        background: rgba(6, 182, 212, 0.2);
        color: #67e8f9;
        font-family: monospace;
        font-size: 0.78rem;
        padding: 3px 8px;
        border-radius: 6px;
        margin: 2px;
        border: 1px solid rgba(6, 182, 212, 0.4);
    }
    
    /* Chat Bubble Enhancements */
    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 12px;
    }
    
    /* Widget Card */
    .widget-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #06b6d4;
        border-radius: 10px;
        padding: 12px;
        margin-top: 8px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Engine in Session State
if "engine" not in st.session_state:
    st.session_state.engine = ChatbotEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "phani_session_" + str(int(time.time()))

if "diagnostics" not in st.session_state:
    st.session_state.diagnostics = {
        "intent": "greeting",
        "confidence_percent": "100%",
        "confidence": 1.0,
        "entities": {},
        "turn_count": 0,
        "latency_ms": 0,
        "sentiment": "Neutral",
        "top_candidates": {"greeting": 1.0},
        "engine_type": "Phani AI Neural Core"
    }

# ----------------------------------------------------
# SIDEBAR - PHANI AI BRANDING, GEMINI KEY & LIVE HUD
# ----------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="brand-badge">
            <span class="project-num">01</span>
            <div>
                <div class="brand-title">PHANI AI</div>
                <div style="font-size: 0.72rem; color: #94a3b8;">Gemini Neural Engine • Python</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Gemini API Key Field (Optional for Real Gemini LLM)
    st.subheader("🔑 Gemini API Key (Optional)")
    gemini_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Optional: Enter your Gemini API key to enable real LLM responses!"
    )

    st.subheader("⚙️ Persona Mode")
    mode_options = {
        "Customer Support": "customer_support",
        "Virtual Assistant": "virtual_assistant",
        "FAQ Automation": "faq_automation"
    }
    selected_mode_label = st.radio(
        "Select Active Persona",
        options=list(mode_options.keys()),
        index=0
    )
    active_mode = mode_options[selected_mode_label]

    st.divider()

    # LIVE NLP DIAGNOSTIC HUD
    st.subheader("⚡ Live Inspector")
    diag = st.session_state.diagnostics

    st.markdown(f"""
        <div class="hud-card">
            <div class="hud-label">Engine Mode</div>
            <div style="color: #34d399; font-weight: 700; font-size: 0.85rem;">{diag.get('engine_type', 'Phani AI Neural Core')}</div>
            <div class="hud-label" style="margin-top: 8px;">Detected Intent</div>
            <div class="intent-val">{diag.get('intent', 'N/A')}</div>
            <div style="font-size: 0.8rem; color: #22d3ee; margin-top: 4px;">Confidence: <strong>{diag.get('confidence_percent', '0%')}</strong></div>
        </div>
    """, unsafe_allow_html=True)

    st.progress(float(diag.get("confidence", 1.0)))

    # Entities
    st.markdown("<div class='hud-label'>Extracted Entities (NER)</div>", unsafe_allow_html=True)
    entities = diag.get("entities", {})
    if entities:
        chips_html = "".join([f"<span class='entity-chip'>{k}: {v}</span>" for k, v in entities.items()])
        st.markdown(f"<div style='margin-bottom: 12px;'>{chips_html}</div>", unsafe_allow_html=True)
    else:
        st.caption("No entities detected")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Turn Count", diag.get("turn_count", 0))
    with col_b:
        st.metric("NLP Latency", f"{diag.get('latency_ms', 0)} ms")

    st.divider()

    if st.button("🔄 Reset Session"):
        st.session_state.engine.reset_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = "phani_session_" + str(int(time.time()))
        st.session_state.diagnostics = {
            "intent": "greeting",
            "confidence_percent": "100%",
            "confidence": 1.0,
            "entities": {},
            "turn_count": 0,
            "latency_ms": 0,
            "sentiment": "Neutral",
            "top_candidates": {"greeting": 1.0},
            "engine_type": "Phani AI Neural Core"
        }
        st.rerun()

    with st.expander("📊 Engine Analytics"):
        analytics = st.session_state.engine.get_analytics()
        st.write(f"**Total Queries:** {analytics['total_requests']}")
        st.write(f"**Avg Latency:** {analytics['avg_latency_ms']} ms")
        if analytics["top_intents"]:
            st.write("**Top Intents:**")
            df = pd.DataFrame(list(analytics["top_intents"].items()), columns=["Intent", "Count"])
            st.dataframe(df, use_container_width=True, hide_index=True)


# ----------------------------------------------------
# MAIN CHAT DISPLAY
# ----------------------------------------------------
st.title(f"✨ PHANI AI - {selected_mode_label}")
st.caption("Trained like real Gemini AI with multi-turn context, intent classification, and real-time generation.")

# Quick Suggestion Chips
st.write("💡 **Quick Suggestions:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💻 Write Python Code"):
        st.session_state.pending_query = "Write a Python script for a fast web scraper."
with col2:
    if st.button("📦 Track Order"):
        st.session_state.pending_query = "Where is my order package ORD-12345?"
with col3:
    if st.button("💳 Request Refund"):
        st.session_state.pending_query = "I want a refund for my billing charge"
with col4:
    if st.button("🧠 Explain AI"):
        st.session_state.pending_query = "Explain how transformer neural networks work."


# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
user_query = None
if "pending_query" in st.session_state:
    user_query = st.session_state.pending_query
    del st.session_state.pending_query
else:
    user_query = st.chat_input("Ask Phani AI anything...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.spinner("Phani AI generating Gemini response..."):
        res = st.session_state.engine.process_message(
            st.session_state.session_id, user_query, mode=active_mode, api_key=gemini_key
        )

    st.session_state.diagnostics = res["diagnostics"]
    bot_msg = {
        "role": "assistant",
        "content": res["response"]
    }
    st.session_state.messages.append(bot_msg)
    st.rerun()