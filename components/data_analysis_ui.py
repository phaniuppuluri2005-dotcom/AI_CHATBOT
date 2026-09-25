"""
Data Analysis & Data Science Studio UI Component for Phani AI.
Interactive workspace for dataset upload (CSV, Excel, JSON), missing value audits, summary KPIs, correlation, and charts.
"""

import streamlit as st
import pandas as pd
from services.data_analysis_service import data_analysis_service


def render_data_analysis_page():
    st.title("📊 Phani AI — Data Analysis & Data Science Studio")
    st.caption("Upload CSV, Excel, or JSON datasets for automated summary statistics, missing value audits, KPI trends, and interactive chart visualizations.")

    uploaded_file = st.file_uploader(
        "Upload Dataset (CSV, Excel, or JSON)",
        type=["csv", "xlsx", "xls", "json"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name

        success, df, msg = data_analysis_service.parse_dataset(file_bytes, filename)

        if not success:
            st.error(msg)
        else:
            st.success(msg)

            # Analyze DataFrame
            analysis = data_analysis_service.analyze_dataframe(df)

            # Overview KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{analysis['total_rows']:,}")
            with col2:
                st.metric("Total Columns", analysis["total_columns"])
            with col3:
                st.metric("Numeric Features", len(analysis["numeric_columns"]))
            with col4:
                total_missing = sum(analysis["missing_values"].values())
                st.metric("Total Missing Values", total_missing)

            st.divider()

            # Data Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Data Preview & Columns",
                "📈 Summary Statistics",
                "⚠️ Missing Values Audit",
                "📊 Interactive Charts",
                "💡 Automated Insights"
            ])

            with tab1:
                st.subheader("Data Preview (First 10 Rows)")
                st.dataframe(df.head(10), use_container_width=True)

                st.subheader("Column Data Types")
                df_types = pd.DataFrame(list(analysis["column_types"].items()), columns=["Column Name", "Data Type"])
                st.dataframe(df_types, use_container_width=True, hide_index=True)

            with tab2:
                st.subheader("Numerical Summary Statistics")
                num_stats = analysis.get("numeric_stats", {})
                if num_stats:
                    df_stats = pd.DataFrame(num_stats).T
                    st.dataframe(df_stats, use_container_width=True)
                else:
                    st.info("No numerical features found in dataset.")

            with tab3:
                st.subheader("Missing Values Audit")
                missing = analysis.get("missing_values", {})
                df_miss = pd.DataFrame(list(missing.items()), columns=["Column Name", "Missing Count"])
                df_miss["Missing Pct (%)"] = (df_miss["Missing Count"] / analysis["total_rows"] * 100).round(2)
                st.dataframe(df_miss, use_container_width=True, hide_index=True)

            with tab4:
                st.subheader("Interactive Visualizations")
                col_chart_type, col_x, col_y = st.columns(3)
                with col_chart_type:
                    chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"])
                with col_x:
                    x_axis = st.selectbox("X-Axis Feature", analysis["columns"], index=0)
                with col_y:
                    y_axis = st.selectbox("Y-Axis Feature", analysis["columns"], index=min(1, len(analysis["columns"]) - 1))

                if chart_type == "Bar Chart":
                    st.bar_chart(df[[x_axis, y_axis]].dropna().set_index(x_axis))
                elif chart_type == "Line Chart":
                    st.line_chart(df[[x_axis, y_axis]].dropna().set_index(x_axis))
                elif chart_type == "Scatter Plot":
                    st.scatter_chart(df[[x_axis, y_axis]].dropna(), x=x_axis, y=y_axis)
                elif chart_type == "Histogram":
                    st.bar_chart(df[x_axis].value_counts())

            with tab5:
                st.subheader("💡 Automated Data Science Insights")
                st.markdown(f"• **Dataset Shape:** `{analysis['total_rows']}` records across `{analysis['total_columns']}` features.")
                if total_missing == 0:
                    st.success("• **Clean Dataset:** No missing values detected in any features!")
                else:
                    st.warning(f"• **Missing Data Notice:** Detected `{total_missing}` missing cells requiring imputation.")
                
                if analysis.get("categorical_insights"):
                    st.markdown("• **Top Categorical Distributions:**")
                    for col_name, top_map in analysis["categorical_insights"].items():
                        top_str = ", ".join([f"{k}: {v}" for k, v in top_map.items()])
                        st.write(f"  - **{col_name}:** {top_str}")
