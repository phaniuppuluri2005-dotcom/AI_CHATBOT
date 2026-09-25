"""
Automated Test Suite for Phani AI Data Analysis Engine.
"""

import pandas as pd
from services.data_analysis_service import data_analysis_service


def test_data_analysis_engine():
    # Sample DataFrame
    data = {
        "Product": ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"],
        "Sales": [1200, 850, 450, 300, 150],
        "Units": [12, 17, 9, 6, 15]
    }
    df = pd.DataFrame(data)

    analysis = data_analysis_service.analyze_dataframe(df)

    assert analysis["success"] is True
    assert analysis["total_rows"] == 5
    assert analysis["total_columns"] == 3
    assert "Sales" in analysis["numeric_columns"]
    assert analysis["numeric_stats"]["Sales"]["mean"] == 590.0
