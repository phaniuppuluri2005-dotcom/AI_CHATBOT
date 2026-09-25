"""
Central AI Orchestrator for Phani AI Platform.
Decomposes complex requests into task pipelines, routes single and multi-intent queries,
executes tool combinations, and synthesizes unified multi-modal user responses.
Fully focused on reliable conversational AI, live real-time services, universal explanations, movie metadata, maps links, and structured data analysis.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from services.web_search_service import web_search_service
from services.router_service import router_service
from services.ai_service import ai_service
from services.weather_service import weather_service
from services.cricket_service import cricket_service
from services.news_service import news_service
from services.stock_service import stock_service
from services.crypto_service import crypto_service
from services.currency_service import currency_service
from services.maps_service import maps_service
from services.movies_service import movies_service
from services.wikipedia_service import wikipedia_service

logger = logging.getLogger("PhaniAI.Orchestrator")


class Orchestrator:
    def detect_multi_intents(self, query: str) -> List[str]:
        """Detect if user query combines multiple tasks (e.g. weather + crypto)."""
        q_lower = query.lower()
        intents = []

        if any(w in q_lower for w in ["research", "deep search", "compare information", "different sources"]):
            intents.append("RESEARCH")

        if any(w in q_lower for w in ["cricket", "criket", "score", "who is winning", "india vs"]):
            intents.append("CRICKET")

        if any(w in q_lower for w in ["weather", "temperature", "rain", "temp"]):
            intents.append("WEATHER")

        if any(w in q_lower for w in ["bitcoin", "crypto", "btc", "eth"]):
            intents.append("CRYPTO")

        if any(w in q_lower for w in ["stock", "share price", "apple stock", "aapl"]):
            intents.append("STOCK_MARKET")

        if any(w in q_lower for w in ["convert", "exchange rate", "forex", "usd to", "inr to", "worth in"]):
            intents.append("CURRENCY")

        if any(w in q_lower for w in ["movie", "film", "cinema", "director of", "cast of", "imdb"]):
            intents.append("MOVIES")

        if any(w in q_lower for w in ["where is", "map of", "location of", "directions to", "near", "nearby"]):
            intents.append("MAPS")

        # Primary intent fallback if no multi-intent matched
        if not intents:
            primary_route = router_service.route_query(query)
            intents.append(primary_route["intent"])

        return list(dict.fromkeys(intents))

    def process_request(
        self,
        query: str,
        previous_context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        persona: str = "virtual_assistant",
        user_preference_style: str = "Balanced"
    ) -> Dict[str, Any]:
        """Execute task pipeline for single or multi-intent user requests."""
        start_time = time.time()
        route = router_service.route_query(query, previous_context)
        detected_intents = self.detect_multi_intents(query)

        primary_intent = route["intent"]
        entities = route["entities"]

        text_response = ""
        cards = []
        services_used = []
        updated_context = dict(previous_context or {})

        # 1. Process Text / Multi-Source Web Research for RESEARCH or CURRENT_INFO intents
        if primary_intent in ["RESEARCH", "CURRENT_INFO"]:
            res_data = web_search_service.search_and_synthesize(query, ai_service)
            text_response = res_data["text_response"]
            services_used.append(res_data.get("provider", "Multi-Source Web Search Engine"))
            cards.append({"type": "RESEARCH", "data": res_data})

        elif primary_intent == "GENERAL_AI" and not any(i in detected_intents for i in ["CRICKET", "CRYPTO", "WEATHER", "CURRENCY", "STOCK_MARKET", "MOVIES", "MAPS"]):
            ai_text = ai_service.generate_response(
                prompt=route.get("resolved_query", query),
                history=history,
                persona=persona,
                user_preference_style=user_preference_style
            )
            if ai_text:
                text_response += ai_text
                services_used.append("Google Gemini LLM")

        # 2. Process Intent Services
        for intent in detected_intents:
            if intent == "RESEARCH" and primary_intent != "RESEARCH":
                res_data = web_search_service.search_and_synthesize(query, ai_service)
                cards.append({"type": "RESEARCH", "data": res_data})
                services_used.append("Multi-Source Web Search")
                if not text_response:
                    text_response = res_data["text_response"]

            elif intent == "CRICKET":
                team = entities.get("team")
                c_data = cricket_service.get_live_scores(query=query, team_filter=team)
                cards.append({"type": "CRICKET", "data": c_data})
                services_used.append("ESPN Cricinfo Live Feed")
                if not c_data.get("success"):
                    text_response = f"Live cricket data is currently unavailable. Please try again shortly."
                else:
                    text_response = f"Here are the latest live cricket match updates (last updated at `{c_data.get('last_updated')}`):"

            elif intent == "WEATHER":
                loc = entities.get("location", "Hyderabad")
                w_data = weather_service.get_weather(loc)
                cards.append({"type": "WEATHER", "data": w_data})
                services_used.append("Open-Meteo Weather API")
                updated_context["last_subject"] = loc
                updated_context["location"] = loc
                if not text_response:
                    if w_data.get("success"):
                        text_response = (
                            f"**{w_data['location']} Weather**\n\n"
                            f"Temperature: {w_data['temperature_c']}°C\n"
                            f"Condition: {w_data['condition']}\n"
                            f"Feels-like: {w_data.get('feels_like_c')}°C\n"
                            f"Humidity: {w_data.get('humidity_pct')}%\n"
                            f"Wind: {w_data['wind_speed_kmh']} km/h\n\n"
                            f"**Last updated:** {w_data['last_updated']}"
                        )
                    else:
                        text_response = f"⚠️ {w_data.get('error', 'Weather data unavailable.')}"

            elif intent == "CRYPTO":
                asset = entities.get("asset", "Bitcoin")
                cr_data = crypto_service.get_crypto_price(asset)
                cards.append({"type": "CRYPTO", "data": cr_data})
                services_used.append("CoinGecko Live Feed")
                updated_context["last_subject"] = asset
                updated_context["asset"] = asset
                if not text_response:
                    if cr_data.get("success"):
                        text_response = (
                            f"**{cr_data['asset']} ({cr_data['symbol']})**\n\n"
                            f"Price: {cr_data['price_usd']} / {cr_data['price_inr']}\n"
                            f"24h Change: {cr_data['change_24h_pct']}% ({cr_data.get('change_24h_inr', '')})\n"
                            f"Market Cap: {cr_data.get('market_cap_usd', 'N/A')}\n\n"
                            f"**Last updated:** {cr_data['last_updated']}"
                        )
                    else:
                        text_response = f"Live {asset} data is currently unavailable."

            elif intent == "STOCK_MARKET":
                symbol = entities.get("symbol", "AAPL")
                s_data = stock_service.get_stock_price(symbol)
                cards.append({"type": "STOCK_MARKET", "data": s_data})
                services_used.append("Yahoo Finance Live Feed")
                if not text_response:
                    text_response = (
                        f"**{s_data['symbol']} — {s_data['company_name']}**\n\n"
                        f"Price: {s_data['price']} {s_data['currency']}\n"
                        f"Change: {s_data['change']} ({s_data['change_pct']}%)\n\n"
                        f"**Last updated:** {s_data['last_updated']}"
                    )

            elif intent == "CURRENCY":
                amount = entities.get("amount", 1.0)
                from_c = entities.get("from_currency", "USD")
                to_c = entities.get("to_currency", "INR")
                hist_date = entities.get("historical_date")
                conv = currency_service.convert(amount, from_c, to_c, historical_date=hist_date)
                cards.append({"type": "CURRENCY", "data": conv})
                services_used.append("Open Exchange Rates Forex API")
                if not text_response:
                    text_response = (
                        f"**{conv['amount']} {conv['from_currency']} = {conv['to_symbol']}{conv['converted_amount']:,.2f}**\n\n"
                        f"Exchange rate:\n**{conv['unit_rate_display']}**\n\n"
                        f"**Rate updated:** {conv['last_updated']}"
                    )

            elif intent == "MOVIES":
                m_data = movies_service.search_movie(query)
                cards.append({"type": "MOVIES", "data": m_data})
                services_used.append("IMDb / OMDb Movie Feed")
                primary = m_data.get("primary_movie") or m_data
                movie_name = primary.get("title", query) if isinstance(primary, dict) else query
                updated_context["last_subject"] = movie_name
                updated_context["movie"] = movie_name

                if not text_response:
                    if m_data.get("success") and m_data.get("movies"):
                        m_list = m_data["movies"]
                        if len(m_list) == 1:
                            m = m_list[0]
                            year_str = f" ({m['year']})" if m.get("year") else ""
                            imdb_link = f"\n\n🔗 [View Full Details on IMDb]({m['imdb_url']})" if m.get("imdb_url") else ""
                            text_response = (
                                f"🎬 **{m['title']}{year_str}**\n\n"
                                f"⭐ **Rating:** {m.get('rating', 'N/A')} | 🏷️ **Genre:** {m.get('genre', 'N/A')}\n"
                                f"🎬 **Director:** {m.get('director', 'N/A')}\n"
                                f"👥 **Cast:** {m.get('actors', 'N/A')}\n\n"
                                f"📖 **Overview:** {m.get('plot', 'No overview available.')}{imdb_link}"
                            )
                        else:
                            resp_parts = [f"Found {len(m_list)} verified movie matches for **'{query}'**:\n"]
                            for idx, m in enumerate(m_list, 1):
                                year_str = f" ({m['year']})" if m.get("year") else ""
                                imdb_link = f" | 🔗 [IMDb]({m['imdb_url']})" if m.get("imdb_url") else ""
                                resp_parts.append(
                                    f"### {idx}. 🎬 {m['title']}{year_str}\n"
                                    f"⭐ **Rating:** {m.get('rating', 'N/A')} | 🏷️ **Genre:** {m.get('genre', 'N/A')}\n"
                                    f"🎬 **Director:** {m.get('director', 'N/A')} | 👥 **Cast:** {m.get('actors', 'N/A')}\n"
                                    f"📖 **Overview:** {m.get('plot', 'No overview available.')}{imdb_link}\n"
                                )
                            text_response = "\n".join(resp_parts)
                    else:
                        text_response = m_data.get("error", f"No verified movie match was found for '{query}'.")

            elif intent == "MAPS":
                user_loc = previous_context.get("user_location") if previous_context else None
                map_data = maps_service.search_location(query, user_location=user_loc)
                cards.append({"type": "MAPS", "data": map_data})
                services_used.append("Google Maps Service")
                updated_context["last_subject"] = map_data.get("display_name", map_data.get("destination"))
                updated_context["location"] = map_data.get("destination")
                if not text_response:
                    dist_info = f"📏 **Distance:** {map_data['distance_km']} km | ⏱️ **Est. Travel Time:** {map_data['duration_min']} min\n\n" if map_data.get('distance_km') else ""
                    orig_info = f" from {map_data['origin']}" if map_data.get('origin') else ""
                    mode_info = f" ({map_data['travel_mode'].capitalize()})" if map_data.get('travel_mode') else ""
                    text_response = (
                        f"🗺️ **{map_data.get('display_name', 'Location Details')}**\n\n"
                        f"{dist_info}"
                        f"📍 [Open Location in Google Maps]({map_data.get('google_maps_url', '')})\n"
                        f"🚗 [Get Directions on Google Maps{orig_info}{mode_info}]({map_data.get('directions_url', '')})"
                    )

            elif intent == "WIKIPEDIA":
                w_res = wikipedia_service.get_summary(query)
                services_used.append("Wikipedia Knowledge API")
                if w_res.get("success") and not text_response:
                    text_response = f"### 📚 {w_res['title']}\n{w_res['summary']}\n\n[Read full article]({w_res['url']})"

        # Fallback response if empty - ALWAYS generate genuine AI response!
        if not text_response:
            text_response = ai_service.generate_response(
                prompt=query,
                history=history,
                persona=persona,
                user_preference_style=user_preference_style
            )

        # Record topic/subject in updated_context
        if "topic" in entities and entities["topic"]:
            updated_context["topic"] = entities["topic"]
            if "last_subject" not in updated_context:
                updated_context["last_subject"] = entities["topic"]

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query,
            "primary_intent": primary_intent,
            "detected_intents": detected_intents,
            "confidence": route["confidence"],
            "confidence_score": route["confidence_score"],
            "entities": entities,
            "text_response": text_response,
            "cards": cards,
            "context": updated_context,
            "latency_ms": elapsed_ms,
            "service_summary": ", ".join(list(dict.fromkeys(services_used))) or "Phani AI Core"
        }


orchestrator = Orchestrator()
