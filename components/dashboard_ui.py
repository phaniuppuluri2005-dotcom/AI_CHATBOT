"""
Admin & Analytics Dashboard UI Component for Phani AI.
Protected by Role-Based Access Control (RBAC). Displays system metrics, query analytics, and benchmark evaluations for Admins.
"""

import streamlit as st
import pandas as pd
from auth.authorization import is_admin
from database.database import SessionLocal
from database.repositories import AnalyticsRepository
from components.eval_ui import render_eval_page


def render_dashboard_page():
    st.title("📊 Phani AI — Protected Admin System & Dashboard")

    # RBAC Security Check
    if not is_admin():
        st.error("🔒 Access Denied: Admin Privileges Required. You must be logged in as an administrator to access the global Admin Dashboard.")
        st.caption("Sign in with an admin account (e.g. `admin@phani.ai` / `adminpassword123`) to unlock administrator metrics.")
        return

    st.caption("Real-time monitoring of system queries, latency, cache hit rates, and quality benchmarks.")

    tab1, tab2 = st.tabs(["📊 Global System Metrics", "🎯 Quality Benchmark Evaluation"])

    with tab1:
        db = SessionLocal()
        try:
            stats = AnalyticsRepository.get_summary_stats(db)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Queries Logged", stats["total_queries"])
            with col2:
                st.metric("Avg Latency", f"{stats['avg_latency_ms']} ms")
            with col3:
                st.metric("Cached Requests", stats["cached_queries"])
            with col4:
                st.metric("Cache Hit Rate", f"{stats['cache_hit_rate_pct']}%")

            st.divider()

            st.subheader("🎯 Query Intent Breakdown")
            intent_data = stats.get("intent_breakdown", {})
            if intent_data:
                df_intent = pd.DataFrame(list(intent_data.items()), columns=["Intent Domain", "Query Count"])
                st.bar_chart(df_intent.set_index("Intent Domain"))
                st.dataframe(df_intent, use_container_width=True, hide_index=True)
            else:
                st.info("No query logs recorded yet.")

        finally:
            db.close()

    with tab2:
        render_eval_page()
