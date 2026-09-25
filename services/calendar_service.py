"""
Calendar & Event Assistance Service for Phani AI.
Provides date calculations, day of week lookup, leap year verification, and event countdowns.
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, Any

logger = logging.getLogger("PhaniAI.CalendarService")


class CalendarService:
    def get_date_info(self, query: str = "today") -> Dict[str, Any]:
        """Process date calculations and calendar queries."""
        now = datetime.now()
        q_lower = query.lower()

        if "tomorrow" in q_lower:
            target_date = now + timedelta(days=1)
        elif "yesterday" in q_lower:
            target_date = now - timedelta(days=1)
        else:
            target_date = now

        day_name = target_date.strftime("%A")
        formatted = target_date.strftime("%B %d, %Y")
        is_leap = (target_date.year % 4 == 0 and (target_date.year % 100 != 0 or target_date.year % 400 == 0))

        return {
            "success": True,
            "query": query,
            "formatted_date": formatted,
            "day_of_week": day_name,
            "iso_date": target_date.strftime("%Y-%m-%d"),
            "is_leap_year": is_leap
        }


calendar_service = CalendarService()
