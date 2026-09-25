"""
Real-Time Live Cricket Data Service for Phani AI.
Fetches live match scores from ESPN Cricinfo RSS feed, classifies status (LIVE, COMPLETED, UPCOMING, NO MATCH),
implements 60s short-lived caching, team filtering, last-updated timestamps, and zero fake score fallbacks.
"""

import time
import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.cache import cache
from config.settings import settings

logger = logging.getLogger("PhaniAI.CricketService")


class CricketService:
    CRICINFO_RSS_URL = "http://static.cricinfo.com/rss/livescores.xml"

    def parse_match_status(self, title: str, description: str) -> str:
        """Classify match status into LIVE, COMPLETED, UPCOMING, or UNKNOWN."""
        desc_lower = description.lower()
        title_lower = title.lower()

        if any(w in desc_lower for w in ["won by", "beat", "match drawn", "tied", "result", "victory"]):
            return "COMPLETED"
        elif any(w in desc_lower for w in ["starts at", "scheduled", "match begins", "yet to begin", "toss"]):
            return "UPCOMING"
        elif any(w in desc_lower for w in ["v", "vs", "ov", "overs", "runs", "wickets", "lead by", "need", "trail by", "*"]):
            return "LIVE"
        return "LIVE" if "*" in title or "ov" in desc_lower else "UNKNOWN"

    def get_live_scores(self, query: str = "", team_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch real-time cricket scores from live RSS feed with 60s short-lived caching,
        team filtering, and last-updated timestamps.
        """
        q_lower = query.lower()
        cache_key = f"live_cricket_{hash(q_lower)}"
        
        # Short-lived TTL cache (max 60 seconds)
        cached = cache.get("cricket", cache_key)
        if cached:
            return cached

        timestamp_str = datetime.now().strftime("%I:%M:%S %p IST, %b %d")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PhaniAI-LiveCricket/2.0"}
            res = requests.get(self.CRICINFO_RSS_URL, headers=headers, timeout=6.0)

            if res.status_code == 200 and len(res.content) > 100:
                root = ET.fromstring(res.content)
                raw_items = root.findall("./channel/item")

                matches = []
                for idx, item in enumerate(raw_items):
                    title = item.find("title").text if item.find("title") is not None else ""
                    description = item.find("description").text if item.find("description") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("guid").text if item.find("guid") is not None else ""

                    if not title or "cricinfo" in title.lower():
                        continue

                    status = self.parse_match_status(title, description)

                    matches.append({
                        "id": f"cric_match_{idx + 1}",
                        "title": title.strip(),
                        "status": status,
                        "score_summary": description.strip(),
                        "link": link.strip(),
                        "last_updated": timestamp_str
                    })

                # Team filtering if user asked for a specific team
                if team_filter:
                    tf_lower = team_filter.lower()
                    filtered = [m for m in matches if tf_lower in m["title"].lower() or tf_lower in m["score_summary"].lower()]
                    if filtered:
                        matches = filtered

                # Historical vs Live filter
                if "yesterday" in q_lower or "completed" in q_lower:
                    matches = [m for m in matches if m["status"] == "COMPLETED"] or matches

                if not matches:
                    return {
                        "success": True,
                        "status_type": "NO MATCH",
                        "last_updated": timestamp_str,
                        "message": "There is currently no live or scheduled cricket match matching your request.",
                        "matches": []
                    }

                result = {
                    "success": True,
                    "status_type": "LIVE" if any(m["status"] == "LIVE" for m in matches) else matches[0]["status"],
                    "provider": "ESPN Cricinfo Live Feed",
                    "last_updated": timestamp_str,
                    "matches": matches[:6]
                }

                cache.set("cricket", cache_key, result, ttl=60)
                return result

        except Exception as e:
            logger.error(f"Live Cricket API connection error: {e}")

        # Explicit failure return (ZERO FAKE DATA)
        return {
            "success": False,
            "status_type": "NO MATCH",
            "last_updated": timestamp_str,
            "error": "Live cricket data is currently unavailable. Please try again shortly."
        }


cricket_service = CricketService()
