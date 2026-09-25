"""
Timezone and DateTime Utilities for Phani AI.
Provides standardized timestamp formatting across all live real-time services.
Format requirement: [Date], [Time] [Timezone] (e.g., '24 Sep 2026, 9:35 PM IST')
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union


def get_current_ist_timestamp() -> str:
    """Returns current date, time and timezone formatted as '24 Sep 2026, 9:35 PM IST'."""
    # IST is UTC+5:30
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_tz)
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%I:%M %p").lstrip('0')
    return f"{date_str}, {time_str} IST"


def format_timestamp(ts: Optional[Union[int, float, str, datetime]] = None) -> str:
    """Format any unix timestamp, ISO string, or datetime object into standard format."""
    if ts is None:
        return get_current_ist_timestamp()

    try:
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts, tz=ist_tz)
        elif isinstance(ts, datetime):
            dt = ts if ts.tzinfo else ts.replace(tzinfo=ist_tz)
        elif isinstance(ts, str):
            # If already nicely formatted, return or convert
            if "IST" in ts or "UTC" in ts or "," in ts:
                return ts
            # Try parsing ISO timestamp
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ist_tz)
        else:
            return get_current_ist_timestamp()

        date_str = dt.strftime("%d %b %Y")
        time_str = dt.strftime("%I:%M %p").lstrip('0')
        return f"{date_str}, {time_str} IST"
    except Exception:
        return get_current_ist_timestamp()
