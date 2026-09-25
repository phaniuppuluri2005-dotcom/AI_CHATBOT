"""
Settings & System Management Component for Phani AI.
Provides API key setup, database path information, cache clearing, and theme preferences.
"""

import os
import streamlit as st
from config.settings import settings
from utils.cache import cache


def render_settings_page():
    st.title("⚙️ Phani AI — Settings & System Configuration")
    st.caption("Configure API keys, model parameters, caching preferences, and database settings.")

    st.subheader("🔑 API Key Credentials")
    gemini_k = st.text_input("Gemini API Key", type="password", value=st.session_state.get("gemini_key", settings.GEMINI_API_KEY))
    if st.button("Save Gemini Key"):
        st.session_state.gemini_key = gemini_k
        os.environ["GEMINI_API_KEY"] = gemini_k
        st.success("API key saved in active session!")

    st.divider()

    st.subheader("💾 Database & System Info")
    st.write(f"• **Database URL:** `{settings.DATABASE_URL}`")
    st.write(f"• **Cache Enabled:** `{settings.CACHE_ENABLED}`")
    st.write(f"• **Cache Default TTL:** `{settings.CACHE_TTL_SECONDS} seconds (15 minutes)`")
    st.write(f"• **Application Version:** `{settings.APP_VERSION}`")

    if st.button("🧹 Clear In-Memory Cache"):
        cache.clear()
        st.success("Memory cache cleared successfully!")
