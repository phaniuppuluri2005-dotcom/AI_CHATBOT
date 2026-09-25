"""
Data Analysis Engine for Phani AI Platform.
Parses CSV, Excel, and JSON datasets in a controlled sandbox using Pandas & NumPy.
Generates missing value audits, summary statistics, top value insights, and chart visualizations.
"""

import io
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("PhaniAI.DataAnalysisService")


class DataAnalysisService:
    def parse_dataset(self, file_bytes: bytes, filename: str) -> Tuple[bool, Any, str]:
        """Parse uploaded dataset into Pandas DataFrame safely."""
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        try:
            if ext == ".csv":
                df = pd.read_csv(io.BytesIO(file_bytes))
                return True, df, f"Successfully loaded CSV dataset '{filename}' ({df.shape[0]} rows, {df.shape[1]} columns)."
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(io.BytesIO(file_bytes))
                return True, df, f"Successfully loaded Excel dataset '{filename}' ({df.shape[0]} rows, {df.shape[1]} columns)."
            elif ext == ".json":
                df = pd.read_json(io.BytesIO(file_bytes))
                return True, df, f"Successfully loaded JSON dataset '{filename}' ({df.shape[0]} rows, {df.shape[1]} columns)."
        except Exception as e:
            logger.error(f"Error parsing dataset {filename}: {e}")
            return False, None, f"Failed to parse dataset: {e}"

        return False, None, f"Unsupported data format '{ext}'. Allowed: .csv, .xlsx, .json"

    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistical summary, missing value audit, and top insights."""
        shape = df.shape
        columns = list(df.columns)
        dtypes = {col: str(df[col].dtype) for col in columns}
        missing_values = df.isnull().sum().to_dict()

        # Numeric columns summary statistics
        numeric_df = df.select_dtypes(include=[np.number])
        numeric_cols = list(numeric_df.columns)
        stats = {}
        if not numeric_df.empty:
            descr = numeric_df.describe().to_dict()
            for col in numeric_cols:
                stats[col] = {
                    "mean": round(descr[col].get("mean", 0.0), 2),
                    "min": round(descr[col].get("min", 0.0), 2),
                    "max": round(descr[col].get("max", 0.0), 2),
                    "std": round(descr[col].get("std", 0.0), 2)
                }

        # Categorical columns top value counts
        cat_df = df.select_dtypes(include=['object', 'category'])
        cat_insights = {}
        for col in cat_df.columns[:5]:
            top_val = df[col].value_counts().head(3).to_dict()
            cat_insights[col] = top_val

        return {
            "success": True,
            "total_rows": shape[0],
            "total_columns": shape[1],
            "columns": columns,
            "column_types": dtypes,
            "missing_values": missing_values,
            "numeric_columns": numeric_cols,
            "numeric_stats": stats,
            "categorical_insights": cat_insights,
            "head_rows": df.head(5).to_dict(orient="records")
        }


data_analysis_service = DataAnalysisService()
