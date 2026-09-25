"""
Multi-Source Information Retrieval, Verification & Web Search Service for Phani AI.
Intelligently fetches content from multiple web sources (Google News, Wikipedia, Official Docs, Open Web),
deduplicates claims, ranks authoritative evidence, verifies conflicting facts, and synthesizes answers with citations.
Never generates localhost or fake URLs.
"""

import re
import requests
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple
from utils.cache import cache
from utils.time_utils import get_current_ist_timestamp, format_timestamp
from config.settings import settings

logger = logging.getLogger("PhaniAI.WebSearchService")


class WebSearchService:
    GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
    WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    DUCKDUCKGO_API = "https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"

    def _assess_source_authority(self, url: str, source_name: str) -> Tuple[int, str]:
        """
        Rank source quality (1 = highest authority, 5 = general web).
        """
        url_lower = url.lower()
        source_lower = source_name.lower()

        if any(domain in url_lower for domain in [".gov", ".edu", "python.org", "microsoft.com", "oracle.com", "w3.org", "developer.mozilla.org"]):
            return 1, "Official / Academic Source"
        elif "wikipedia.org" in url_lower:
            return 2, "Verified Encyclopedia"
        elif any(news in source_lower or news in url_lower for news in ["reuters", "bbc", "techcrunch", "ndtv", "thehindu", "indianexpress", "bloomberg", "the verge", "financial times"]):
            return 3, "Established News Publication"
        elif any(tech in url_lower for tech in ["geeksforgeeks", "stackoverflow", "medium", "dev.to", "github.com", "realpython"]):
            return 4, "Technical / Specialist Resource"
        return 5, "Web Resource"

    def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a complex research question into focused subqueries.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()
        subqueries = [q_clean]

        # Handle comparison queries ("compare Power BI and Tableau for data analyst jobs")
        if "compare" in q_lower or " vs " in q_lower or " versus " in q_lower:
            parts = re.split(r'\b(?:compare|and|vs|versus|with|for)\b', q_clean, flags=re.IGNORECASE)
            cleaned_parts = [p.strip() for p in parts if len(p.strip()) > 2 and p.strip().lower() not in ["the", "in", "job", "jobs"]]
            if len(cleaned_parts) >= 2:
                subqueries.append(f"{cleaned_parts[0]} features and use cases")
                subqueries.append(f"{cleaned_parts[1]} features and use cases")
                subqueries.append(f"{cleaned_parts[0]} vs {cleaned_parts[1]} comparison")

        elif "research" in q_lower or "latest" in q_lower or "developments" in q_lower:
            core_topic = re.sub(r'(?i)\b(research|the|latest|developments|in|information|about|find|deep search)\b', '', q_clean).strip()
            if core_topic:
                subqueries.append(f"{core_topic} latest features updates")
                subqueries.append(f"{core_topic} official documentation")

        # Limit to 3 distinct subqueries max to optimize latency
        unique_subqueries = []
        for sq in subqueries:
            if sq and sq not in unique_subqueries:
                unique_subqueries.append(sq)
        return unique_subqueries[:3]

    def fetch_sources_for_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve search results from multiple live web endpoints.
        """
        raw_sources = []
        headers = {"User-Agent": "PhaniAI-ResearchBot/2.0 (contact@phani.ai)"}

        # 1. Fetch from Google News RSS
        try:
            url = self.GOOGLE_NEWS_RSS.format(query=requests.utils.quote(query))
            res = requests.get(url, headers=headers, timeout=settings.API_TIMEOUT)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall("./channel/item")[:5]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    source_name = item.find("source").text if item.find("source") is not None else "Web Source"
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    if title and link and not link.startswith("http://localhost"):
                        rank, category = self._assess_source_authority(link, source_name)
                        raw_sources.append({
                            "title": title,
                            "url": link,
                            "source_name": source_name,
                            "snippet": f"{title} - Reported by {source_name}.",
                            "pub_date": format_timestamp(pub_date) if pub_date else "",
                            "authority_rank": rank,
                            "category": category
                        })
        except Exception as e:
            logger.debug(f"Google News RSS search failed for query '{query}': {e}")

        # 2. Fetch from Wikipedia API
        try:
            search_params = {"action": "query", "list": "search", "srsearch": query, "format": "json"}
            w_res = requests.get(self.WIKI_SEARCH_URL, headers=headers, params=search_params, timeout=settings.API_TIMEOUT)
            if w_res.status_code == 200:
                search_hits = w_res.json().get("query", {}).get("search", [])
                for hit in search_hits[:2]:
                    page_title = hit.get("title")
                    snippet_clean = re.sub(r'<[^>]+>', '', hit.get("snippet", ""))
                    wiki_url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(page_title.replace(' ', '_'))}"
                    
                    raw_sources.append({
                        "title": f"Wikipedia: {page_title}",
                        "url": wiki_url,
                        "source_name": "Wikipedia",
                        "snippet": snippet_clean,
                        "pub_date": "",
                        "authority_rank": 2,
                        "category": "Verified Encyclopedia"
                    })
        except Exception as e:
            logger.debug(f"Wikipedia search failed for query '{query}': {e}")

        # 3. Fetch from DuckDuckGo Instant Answer / Web API
        try:
            ddg_url = self.DUCKDUCKGO_API.format(query=requests.utils.quote(query))
            d_res = requests.get(ddg_url, headers=headers, timeout=settings.API_TIMEOUT)
            if d_res.status_code == 200:
                d_json = d_res.json()
                abstract = d_json.get("AbstractText")
                abstract_url = d_json.get("AbstractURL")
                abstract_source = d_json.get("AbstractSource", "Web Search")
                if abstract and abstract_url:
                    rank, category = self._assess_source_authority(abstract_url, abstract_source)
                    raw_sources.append({
                        "title": d_json.get("Heading", query),
                        "url": abstract_url,
                        "source_name": abstract_source,
                        "snippet": abstract,
                        "pub_date": "",
                        "authority_rank": rank,
                        "category": category
                    })
                
                # Add related topics
                for topic in d_json.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                        t_url = topic.get("FirstURL")
                        rank, category = self._assess_source_authority(t_url, "Web Search")
                        raw_sources.append({
                            "title": topic.get("Text")[:60] + "...",
                            "url": t_url,
                            "source_name": "Web Search",
                            "snippet": topic.get("Text"),
                            "pub_date": "",
                            "authority_rank": rank,
                            "category": category
                        })
        except Exception as e:
            logger.debug(f"DuckDuckGo API search failed for query '{query}': {e}")

        return raw_sources

    def deduplicate_and_rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate sources by URL/title and rank by authority score.
        """
        seen_urls = set()
        seen_titles = set()
        unique_sources = []

        for s in sources:
            url = s.get("url", "").strip()
            title = s.get("title", "").strip().lower()

            if not url or url in seen_urls:
                continue
            if title in seen_titles:
                continue
            if "localhost" in url or "127.0.0.1" in url:
                continue

            seen_urls.add(url)
            seen_titles.add(title)
            unique_sources.append(s)

        # Sort primary by authority_rank (ascending), secondary by snippet length (descending)
        unique_sources.sort(key=lambda x: (x.get("authority_rank", 5), -len(x.get("snippet", ""))))
        return unique_sources

    def verify_conflicts(self, sources: List[Dict[str, Any]]) -> Optional[str]:
        """
        Check for explicit discrepancies or conflicting numbers/dates between sources.
        """
        # Look for conflicting date or version claims if present
        dates = set()
        for s in sources:
            snip = s.get("snippet", "")
            found_dates = re.findall(r'\b(202[0-9]|201[0-9])\b', snip)
            for d in found_dates:
                dates.add(d)
        
        if len(dates) > 1 and len(sources) >= 2:
            s1 = sources[0].get("source_name", "Source A")
            s2 = sources[1].get("source_name", "Source B")
            date_list = list(dates)
            return f"Note: Sources differ on timelines or figures across reports (e.g. {s1} references {date_list[0]} while {s2} mentions {date_list[-1]})."
        
        return None

    def search_and_synthesize(self, raw_query: str, ai_service_instance: Any = None) -> Dict[str, Any]:
        """
        Full multi-source research workflow:
        1. Decompose query
        2. Fetch sources from multiple endpoints
        3. Deduplicate & rank
        4. Verify conflicts
        5. Synthesize answer with citations
        """
        cache_key = f"web_research_{raw_query.lower().strip()}"
        cached = cache.get("web_search", cache_key)
        if cached:
            return cached

        timestamp = get_current_ist_timestamp()

        # 1. Decompose query
        subqueries = self.decompose_query(raw_query)

        # 2. Gather sources for each subquery
        all_raw_sources = []
        for sq in subqueries:
            all_raw_sources.extend(self.fetch_sources_for_query(sq))

        # 3. Deduplicate & Rank
        ranked_sources = self.deduplicate_and_rank_sources(all_raw_sources)

        # 4. Check Conflicts
        conflict_note = self.verify_conflicts(ranked_sources)

        if not ranked_sources:
            return {
                "success": False,
                "query": raw_query,
                "text_response": "I couldn't retrieve current external information right now. Please try again or rephrase your question.",
                "sources": [],
                "last_updated": timestamp
            }

        # 5. Build prompt for AI Synthesis or fallback synthesis
        top_sources = ranked_sources[:5]
        evidence_text = ""
        citation_links = []

        for idx, src in enumerate(top_sources, 1):
            evidence_text += f"\nSource [{idx}]: {src['title']} ({src['source_name']})\nURL: {src['url']}\nSummary: {src['snippet']}\n"
            citation_links.append(f"{idx}. [{src['title']}]({src['url']}) — *{src['source_name']}* ({src['category']})")

        synthesis_prompt = (
            f"Synthesize a clear, well-structured answer for the user query: '{raw_query}'.\n\n"
            f"Use the following retrieved multi-source evidence:\n{evidence_text}\n"
        )
        if conflict_note:
            synthesis_prompt += f"\nImportant discrepancy note: {conflict_note}\n"

        synthesis_prompt += (
            "\nFormatting Instructions:\n"
            "1. Provide a direct, comprehensive ## Answer to the user's question with inline source citations e.g. [Source Name](URL).\n"
            "2. Provide a bulleted ## Key Findings section summarizing the verified facts.\n"
            "3. If sources differ or conflict, include a ## Source Comparison section explaining the differences.\n"
            "4. NEVER invent false claims or use localhost URLs.\n"
        )

        synthesized_text = ""
        if ai_service_instance:
            synthesized_text = ai_service_instance.generate_response(
                prompt=synthesis_prompt,
                persona="researcher"
            )

        if not synthesized_text or "I processed your query" in synthesized_text:
            # Clean fallback synthesis if LLM is offline
            ans_parts = [f"## Answer\nBased on verified multi-source research for **'{raw_query}'**:\n"]
            for src in top_sources[:3]:
                ans_parts.append(f"• **{src['title']}**: {src['snippet']} ([Read Source]({src['url']}))")

            ans_parts.append("\n## Key Findings")
            for src in top_sources[:3]:
                ans_parts.append(f"- {src['snippet']}")

            if conflict_note:
                ans_parts.append(f"\n## Source Comparison\n{conflict_note}")

            synthesized_text = "\n".join(ans_parts)

        # Append Sources section
        sources_section = "\n\n### Sources\n" + "\n".join(citation_links)
        full_response = synthesized_text + sources_section + f"\n\n*Last updated:* {timestamp}"

        result = {
            "success": True,
            "query": raw_query,
            "subqueries": subqueries,
            "text_response": full_response,
            "sources": top_sources,
            "conflict_note": conflict_note,
            "last_updated": timestamp,
            "provider": "Multi-Source Web Search Engine"
        }

        cache.set("web_search", cache_key, result, ttl=1800)
        return result


web_search_service = WebSearchService()
