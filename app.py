"""
Phani AI — Reliable Universal AI Platform
Main Application Entrypoint built with Streamlit, Python NLP, Google Gemini, and Real-Time Services.
"""

import os
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Phani AI - Universal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Dark Cobalt & Cyan Aesthetic CSS
from components.styles import CUSTOM_CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Render Sidebar & Get Active Page
from components.sidebar import render_sidebar
current_page = render_sidebar()

# Page Routing
from components.chat_ui import render_chat_interface
from components.live_services_ui import render_live_services_page
from components.data_analysis_ui import render_data_analysis_page
from components.student_ui import render_student_page
from components.history_ui import render_history_page
from components.dashboard_ui import render_dashboard_page
from components.settings_ui import render_settings_page

if current_page == "🏠 Home":
    st.title("🤖 Welcome to Phani AI Assistant")
    st.markdown("""
        > **Phani AI** is a universal AI assistant that combines general AI conversation, universal knowledge explanations,
        > live real-time information, structured data analysis, coding assistance, and intelligent tool orchestration.
    """)

    st.markdown("""
        ### ⚡ Core Platform Capabilities
        
        | Capability | Service Description |
        | :--- | :--- |
        | 💬 **Conversational AI** | Multi-turn reasoning powered by Google Gemini LLM with context retention |
        | 🎯 **Query Orchestrator** | Multi-intent task planner & typo-tolerant routing across real-time & knowledge domains |
        | 🌐 **Live Real-Time Data** | Current Weather, Cricket Scores, Bitcoin/Crypto, Universal Forex, News & Stocks |
        | 📊 **Data Science Engine** | Structured CSV/Excel/JSON dataset analysis, automated statistical audit & Plotly charts |
        | 🎓 **Universal Explanations** | Concept explanations, coding assistance, math problem solving, and dynamic quizzes |
        | 🔒 **Security & Isolation** | User account authentication, RBAC admin controls, and server-side data isolation |
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💬 Launch Main AI Chat", use_container_width=True):
            st.session_state.current_page = "💬 AI Chat"
            st.rerun()
    with col2:
        if st.button("📊 Analyze Structured Dataset (CSV/Excel)", use_container_width=True):
            st.session_state.current_page = "📊 Data Analysis"
            st.rerun()
    with col3:
        if st.button("🌐 Explore Live Services", use_container_width=True):
            st.session_state.current_page = "🌐 Live Services"
            st.rerun()

elif current_page == "💬 AI Chat":
    render_chat_interface()

elif current_page == "🌐 Live Services":
    render_live_services_page()

elif current_page == "📊 Data Analysis":
    render_data_analysis_page()

elif current_page == "🎓 Student Assistant":
    render_student_page()

elif current_page == "🕘 History & Saved":
    render_history_page()

elif current_page == "📊 Admin Dashboard":
    render_dashboard_page()

elif current_page == "⚙️ Settings":
    render_settings_page()
