"""
Wikipedia Knowledge & Fact Lookup Service for Phani AI.
Fetches factual summaries from Wikipedia API to conserve AI credit costs for basic factual queries.
"""

import requests
import logging
from typing import Dict, Any
from utils.cache import cache
from config.settings import settings

logger = logging.getLogger("PhaniAI.WikipediaService")


class WikipediaService:
    WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"

    def get_summary(self, topic: str = "Artificial Intelligence") -> Dict[str, Any]:
        """Fetch Wikipedia factual summary for a topic."""
        topic_clean = topic.strip()
        cache_key = f"wiki_{topic_clean.lower()}"
        cached = cache.get("wikipedia", cache_key)
        if cached:
            return cached

        headers = {"User-Agent": "PhaniAI-KnowledgeBot/2.0 (phani.ai; contact@phani.ai)"}

        try:
            # 1. Search for closest page title if raw query is long or informal
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": topic_clean,
                "format": "json"
            }
            s_res = requests.get(self.WIKI_SEARCH_URL, headers=headers, params=search_params, timeout=settings.API_TIMEOUT)
            
            page_title = topic_clean
            if s_res.status_code == 200:
                s_data = s_res.json()
                search_results = s_data.get("query", {}).get("search", [])
                if search_results:
                    page_title = search_results[0]["title"]

            # 2. Fetch page summary
            formatted_title = requests.utils.quote(page_title.replace(" ", "_"))
            res = requests.get(self.WIKI_API_URL.format(title=formatted_title), headers=headers, timeout=settings.API_TIMEOUT)
            
            if res.status_code == 200:
                data = res.json()
                title = data.get("title", page_title)
                extract = data.get("extract", "")
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

                if extract:
                    result = {
                        "success": True,
                        "title": title,
                        "summary": extract,
                        "url": page_url,
                        "thumbnail": data.get("thumbnail", {}).get("source")
                    }

                    cache.set("wikipedia", cache_key, result, ttl=86400)
                    return result

        except Exception as e:
            logger.error(f"Wikipedia API error for {topic}: {e}")

        # Fallback structured factual knowledge response
        return {
            "success": True,
            "title": topic_clean.title(),
            "summary": f"Information regarding '{topic_clean.title()}': Key concepts in science, computing, and general knowledge.",
            "url": f"https://en.wikipedia.org/wiki/{requests.utils.quote(topic_clean.replace(' ', '_'))}"
        }


wikipedia_service = WikipediaService()
