"""
Real-Time News & Topic Search Service for Phani AI.
Fetches latest headlines, tech news, business, sports, and query search using open RSS / News APIs.
Ensures exact live date/time timestamps on articles.
"""

import requests
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List
from utils.cache import cache
from utils.time_utils import get_current_ist_timestamp, format_timestamp
from config.settings import settings

logger = logging.getLogger("PhaniAI.NewsService")


class NewsService:
    RSS_URL = "https://news.google.com/rss/search?q={topic}&hl=en-IN&gl=IN&ceid=IN:en"

    def get_news(self, topic: str = "technology") -> Dict[str, Any]:
        """Fetch latest news articles for a given topic with timestamps."""
        cache_key = f"news_{topic.lower()}"
        cached = cache.get("news", cache_key)
        if cached:
            return cached

        last_updated_time = get_current_ist_timestamp()

        try:
            url = self.RSS_URL.format(topic=requests.utils.quote(topic))
            res = requests.get(url, timeout=settings.API_TIMEOUT)
            
            articles = []
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall("./channel/item")[:8]:
                    title = item.find("title").text if item.find("title") is not None else "News Title"
                    link = item.find("link").text if item.find("link") is not None else ""
                    raw_pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    source = item.find("source").text if item.find("source") is not None else "Global News"

                    formatted_date = format_timestamp(raw_pub_date) if raw_pub_date else last_updated_time

                    articles.append({
                        "title": title,
                        "source": source,
                        "pub_date": formatted_date,
                        "link": link,
                        "summary": f"Latest report on {topic} from {source}."
                    })

            result = {
                "success": True,
                "topic": topic,
                "count": len(articles),
                "articles": articles,
                "last_updated": last_updated_time,
                "provider": "Google News Live Feed"
            }

            cache.set("news", cache_key, result, ttl=1800)
            return result

        except Exception as e:
            logger.error(f"Error fetching news for topic {topic}: {e}")
            return {
                "success": False,
                "topic": topic,
                "articles": [],
                "error": "News service temporarily unavailable.",
                "last_updated": last_updated_time,
                "provider": "Google News Live Feed"
            }


news_service = NewsService()
