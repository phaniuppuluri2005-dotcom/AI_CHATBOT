"""
Sidebar Navigation & Auth Status Component for Phani AI.
Provides authentication status, destination routing, persona modes, and live inspector HUD.
"""

import os
import time
import streamlit as st
from auth.authentication import get_current_user_dict
from components.auth_ui import render_auth_modal


def render_sidebar():
    with st.sidebar:
        # Branding Header
        st.markdown("""
            <div class="brand-badge">
                <span class="project-num">01</span>
                <div>
                    <div class="brand-title">PHANI AI</div>
                    <div style="font-size: 0.72rem; color: #94a3b8;">Universal AI Assistant</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Authentication Status
        render_auth_modal()
        st.divider()

        # Navigation Menu Options
        st.subheader("🧭 Platform Navigation")
        nav_options = [
            "🏠 Home",
            "💬 AI Chat",
            "📊 Data Analysis",
            "🌐 Live Services",
            "🎓 Student Assistant",
            "🕘 History & Saved",
            "📊 Admin Dashboard",
            "⚙️ Settings"
        ]

        if "current_page" not in st.session_state or st.session_state.current_page not in nav_options:
            st.session_state.current_page = "💬 AI Chat"

        selected_page = st.radio(
            "Select Destination",
            options=nav_options,
            index=nav_options.index(st.session_state.current_page)
        )
        st.session_state.current_page = selected_page

        st.divider()

        # Gemini API Key Field
        st.subheader("🔑 Gemini API Key")
        gemini_key = st.text_input(
            "API Key (Optional)",
            type="password",
            value=st.session_state.get("gemini_key", os.environ.get("GEMINI_API_KEY", "")),
            help="Enter your Google Gemini API key for active LLM generation."
        )
        st.session_state.gemini_key = gemini_key

        # Active Persona & Response Length Settings
        st.subheader("⚙️ Persona & Length Preferences")
        persona_map = {
            "Virtual Assistant": "virtual_assistant",
            "Customer Support": "customer_support",
            "FAQ Automation": "faq_automation"
        }
        selected_persona = st.selectbox("Active Persona", list(persona_map.keys()), index=0)
        st.session_state.active_persona = persona_map[selected_persona]

        response_lengths = ["Balanced", "Brief", "Detailed"]
        st.session_state.user_preference_style = st.selectbox("Default Response Length", response_lengths, index=0)

        st.divider()

        # LIVE NLP INSPECTOR HUD
        st.subheader("⚡ Live Inspector HUD")
        diag = st.session_state.get("diagnostics", {
            "intent": "GENERAL_AI",
            "confidence": "HIGH",
            "confidence_score": 1.0,
            "entities": {},
            "latency_ms": 0.0,
            "service": "Phani AI Orchestrator"
        })

        st.markdown(f"""
            <div class="hud-card">
                <div class="hud-label">Service Provider</div>
                <div style="color: #34d399; font-weight: 700; font-size: 0.85rem;">{diag.get('service', 'Phani AI Orchestrator')}</div>
                <div class="hud-label" style="margin-top: 8px;">Routed Intent</div>
                <div class="intent-val">{diag.get('intent', 'GENERAL_AI')}</div>
                <div style="font-size: 0.8rem; color: #22d3ee; margin-top: 4px;">Confidence: <strong>{diag.get('confidence', 'HIGH')} ({int(diag.get('confidence_score', 1.0)*100)}%)</strong></div>
            </div>
        """, unsafe_allow_html=True)

        st.progress(float(diag.get("confidence_score", 1.0)))

        st.divider()

        # Session Reset Button
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.session_id = f"phani_session_{int(time.time())}"
            st.session_state.previous_context = {}
            st.session_state.diagnostics = {
                "intent": "GENERAL_AI",
                "confidence": "HIGH",
                "confidence_score": 1.0,
                "entities": {},
                "latency_ms": 0.0,
                "service": "Phani AI Orchestrator"
            }
            st.rerun()

        return selected_page
