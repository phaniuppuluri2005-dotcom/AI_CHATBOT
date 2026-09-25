"""
Admin Quality Control Benchmark Evaluation System UI Component for Phani AI.
Restricted strictly to administrators for measuring factual accuracy, intent routing, latency, and failure rates.
"""

import streamlit as st
import pandas as pd
from auth.authorization import is_admin
from services.eval_service import eval_service


def render_eval_page():
    st.title("🎯 Phani AI — Admin Benchmark & Quality Evaluation System")
    st.caption("Restricted Administrator Tool: Measures intent routing accuracy, entity extraction precision, API latency, and failure rates across standard benchmarks.")

    # RBAC Authorization Check
    if not is_admin():
        st.error("🔒 Access Denied: Admin Privileges Required. You must be logged in as an administrator to run evaluation benchmarks.")
        return

    if st.button("🚀 Run Full System Evaluation Benchmark", use_container_width=True):
        with st.spinner("Running Benchmark Evaluation Test Suite across Intent, Routing, and Latency..."):
            report = eval_service.run_benchmark_suite()

            st.success("Benchmark Evaluation Complete!")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Benchmark Tests", report["total_benchmark_tests"])
            with col2:
                st.metric("Intent Accuracy Rate", f"{report['intent_accuracy_pct']}%")
            with col3:
                st.metric("Entity Extraction Rate", f"{report['entity_accuracy_pct']}%")
            with col4:
                st.metric("Avg Response Latency", f"{report['avg_response_latency_ms']} ms")

            st.divider()

            st.subheader("📋 Detailed Benchmark Test Results")
            df_res = pd.DataFrame(report["detailed_results"])
            st.dataframe(df_res, use_container_width=True, hide_index=True)
