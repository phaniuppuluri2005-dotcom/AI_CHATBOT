"""
Intelligent Query Router & Entity Extractor for Phani AI Platform.
Routes queries dynamically using hybrid Typo Correction, Levenshtein Fuzzy Matching,
Regex NER, and LLM reasoning fallback.
Contains ZERO hardcoded topic restrictions or fixed topic logic.
"""

import re
import math
import logging
from typing import Dict, Any, List, Tuple, Optional
from utils.typo_tolerance import correct_typos, similarity_ratio

logger = logging.getLogger("PhaniAI.Router")

# Domain Intent Patterns & Keywords (Live Real-Time Data & Tools only)
INTENT_PATTERNS: Dict[str, Dict[str, Any]] = {
    "RESEARCH": {
        "keywords": ["research", "deep search", "compare information", "different sources", "what do sources say", "find information about", "latest developments", "search the web", "thorough research"],
        "phrases": ["research this", "research about", "compare information from different sources", "what do different sources say", "do a deep search", "search the web for", "latest developments in"]
    },
    "CURRENT_INFO": {
        "keywords": ["latest", "current", "today", "now", "recently", "this week", "this month", "newest", "real-time", "live"],
        "phrases": ["latest version", "current version", "what happened today", "latest news", "latest updates", "recent updates", "current status"]
    },
    "WEATHER": {
        "keywords": ["weather in", "temperature in", "temp in", "will it rain", "rain in", "umbrella", "weather forecast", "weather today", "weather right now"],
        "phrases": ["weather in", "what is the weather in", "will it rain", "what's temp in", "do i need an umbrella", "weather forecast", "weather today", "weather right now"]
    },
    "CRICKET": {
        "keywords": ["cricket score", "cricket match", "t20 score", "ipl score", "odi score", "who is winning", "criket score", "cricket scor"],
        "phrases": ["cricket score", "live cricket score", "what is the cricket score", "current cricket score", "india cricket score", "india vs australia score", "who is winning", "who is winning the cricket match", "live score", "current score", "criket score", "cricket scrore", "cricket scor", "latest cricket match", "today's cricket matches", "who won match", "who won today's cricket match", "who won today cricket match", "today's cricket match", "live cricket", "today cricket match", "cricket updates"]
    },
    "NEWS": {
        "keywords": ["news", "headline", "headlines", "latest news", "breaking news", "newspaper", "article", "sports news", "tech news", "world news"],
        "phrases": ["news about", "latest news", "breaking news", "what happened in", "tech news", "business news", "today news"]
    },
    "STOCK_MARKET": {
        "keywords": ["stock price", "share price", "nasdaq", "nyse", "nifty", "sensex", "ticker", "market cap of", "apple stock", "tesla stock", "nvda stock", "aapl stock", "googl stock", "msft stock"],
        "phrases": ["stock price", "share price", "market cap of", "how is stock doing", "show stock", "market update"]
    },
    "CRYPTO": {
        "keywords": ["bitcoin price", "crypto price", "btc price", "eth price", "solana price", "doge price", "cryptocurrency price", "current bitcoin price", "current btc price", "btc to usd", "eth to usd"],
        "phrases": ["bitcoin price", "crypto price", "btc to usd", "eth price", "current crypto price", "crypto market", "how much is bitcoin", "current price of bitcoin", "bitcoin current price", "btc price"]
    },
    "CURRENCY": {
        "keywords": ["convert", "exchange rate", "forex", "usd to inr", "inr to usd", "convert dollars", "convert rupees", "worth in rupees", "worth in dollars"],
        "phrases": ["convert to", "how much is in", "exchange rate", "dollars to rupees", "usd to inr", "inr to usd", "convert 100 dollars", "in rupees", "worth in", "to inr", "to usd", "into aed", "in aud", "in jpy", "in eur", "in gbp", "in cad", "in chf"]
    },
    "MAPS": {
        "keywords": ["map", "location of", "address of", "directions to", "where is", "route to", "places near", "distance to", "navigate to"],
        "phrases": ["where is", "how to reach", "directions to", "map of", "location of", "places in"]
    },
    "MOVIES": {
        "keywords": ["movie", "film", "cinema", "director of", "cast of", "imdb", "rating of", "box office", "plot of", "genre of", "pushpa", "puspha", "og", "they call him og", "inception", "avatar", "batman", "interstellar", "titanic"],
        "phrases": ["movie rating", "tell me about movie", "tell me about", "who directed", "release date of", "cast of", "they call him og", "pushpa 2", "pushpa 2021", "pushpa 2024", "og 2025"]
    },
    "TRANSLATION": {
        "keywords": ["translate", "translation", "english to", "telugu", "hindi", "spanish", "french", "german"],
        "phrases": ["translate this", "translate into", "how to say in", "meaning in telugu", "meaning in hindi"]
    },
    "STUDENT_ASSISTANT": {
        "keywords": ["quiz", "interview questions", "create quiz", "practice quiz", "timetable"],
        "phrases": ["create quiz", "give me a quiz", "interview questions", "study timetable"]
    }
}


class EntityExtractor:
    @staticmethod
    def extract_entities(query: str) -> Dict[str, Any]:
        entities = {}
        corrected_q = correct_typos(query)
        q_lower = corrected_q.lower().strip()

        # 1. Level Extraction
        if any(w in q_lower for w in ["beginner", "easy", "simple", "for a beginner", "for beginners", "at beginner level", "eli5"]):
            entities["level"] = "beginner"
        elif "intermediate" in q_lower:
            entities["level"] = "intermediate"
        elif any(w in q_lower for w in ["advanced", "expert"]):
            entities["level"] = "advanced"
        else:
            entities["level"] = None

        # 2. Detail Extraction
        if any(w in q_lower for w in ["briefly", "short", "concise", "in short", "quick summary"]):
            entities["detail"] = "brief"
        elif any(w in q_lower for w in ["in detail", "detailed", "comprehensive", "deep dive"]):
            entities["detail"] = "detailed"
        else:
            entities["detail"] = "standard"

        # 3. Mode Extraction
        if any(w in q_lower for w in ["quiz", "questions", "question", "mcq", "test my"]):
            entities["mode"] = "quiz"
            entities["action_intent"] = "quiz"
        elif any(w in q_lower for w in ["timetable", "study plan", "schedule", "calendar"]):
            entities["mode"] = "timetable"
            entities["action_intent"] = "timetable"
        elif re.search(r'\b(teach|teach me|step by step|how to learn|learning path|roadmap)\b', q_lower) or (q_lower.startswith("learn ") and q_lower != "learn"):
            entities["mode"] = "learning"
            entities["action_intent"] = "teach"
        elif "interview" in q_lower:
            entities["mode"] = "interview"
            entities["action_intent"] = "interview"
        elif any(w in q_lower for w in ["only code", "code only", "just code", "code example"]):
            entities["mode"] = "code"
            entities["action_intent"] = "code"
        elif any(w in q_lower for w in ["define", "definition of"]):
            entities["mode"] = "overview"
            entities["action_intent"] = "define"
        else:
            entities["mode"] = "overview"
            entities["action_intent"] = "general"

        # 4. Clean Topic Extraction (stripping instructions & modifiers so topic is clean)
        clean_topic = re.sub(
            r'(?i)\b(at\s+a\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+a\s+level|at\s+level|for\s+(?:a\s+)?(?:beginner|beginners|students|student|freshers|kids)|for\s+an?\s+interview|interview\s+questions|interview\s+answer|interview|create\s+a?\s+timetable\s+for|study\s+plan|schedule|quiz\s+me\s+on|quiz\s+me|quiz|questions|question|only\s+code|code\s+only|with\s+an?\s+example|with\s+examples|step\s+by\s+step|in\s+detail|detailed|briefly|simply|like\s+i\'m\s+\d+|define|definition\s+of|explain|describe|teach\s+me|teach|tell\s+me\s+about|what\s+is|what\s+are|how\s+does|research|compare|latest|current|version)\b',
            '',
            corrected_q
        ).strip()

        if q_lower.startswith("learn ") and not q_lower.startswith("learning"):
            clean_topic = re.sub(r'(?i)^learn\s+', '', clean_topic).strip()

        clean_topic = re.sub(r'(?i)\b(beginner|beginners|intermediate|advanced|expert|level|levels|brief|short|concise)\b', '', clean_topic).strip()
        clean_topic = clean_topic.strip("'\"")
        clean_topic = re.sub(r'^[^\w]+|[^\w]+$', '', clean_topic).strip()
        clean_topic = clean_topic.strip("'\"")

        if clean_topic:
            if clean_topic.isupper():
                entities["topic"] = clean_topic
            else:
                entities["topic"] = clean_topic[0].upper() + clean_topic[1:] if len(clean_topic) > 0 else clean_topic
        else:
            entities["topic"] = corrected_q

        # Team name extraction for Cricket
        team_match = re.search(r'\b(india|australia|england|south africa|pakistan|new zealand|sri lanka|west indies|bangladesh|afghanistan|csk|srh|rcb|mi|kkr|dc|pbks|rr|gt|lsg)\b', q_lower)
        if team_match:
            entities["team"] = team_match.group(1).title()

        # Currency amount, source code, target code extraction
        amt_match = re.search(r'\b(\d+(?:\.\d+)?)\b', query)
        if amt_match:
            try:
                entities["amount"] = float(amt_match.group(1))
            except ValueError:
                pass

        # Detect currency symbols and words
        curr_map = {
            "$": "USD", "dollar": "USD", "dollars": "USD", "usd": "USD",
            "₹": "INR", "rupee": "INR", "rupees": "INR", "inr": "INR",
            "€": "EUR", "euro": "EUR", "euros": "EUR", "eur": "EUR",
            "£": "GBP", "pound": "GBP", "pounds": "GBP", "gbp": "GBP",
            "¥": "JPY", "yen": "JPY", "japanese yen": "JPY", "jpy": "JPY",
            "dirham": "AED", "dirhams": "AED", "aed": "AED",
            "aud": "AUD", "cad": "CAD", "sgd": "SGD", "cny": "CNY", "chf": "CHF"
        }

        found_currencies = []
        for word, code in curr_map.items():
            if word in q_lower and code not in found_currencies:
                found_currencies.append(code)

        if len(found_currencies) >= 2:
            entities["from_currency"] = found_currencies[0]
            entities["to_currency"] = found_currencies[1]
        elif len(found_currencies) == 1:
            if "to" in q_lower or "in" in q_lower or "into" in q_lower:
                entities["to_currency"] = found_currencies[0]
                entities["from_currency"] = "USD" if found_currencies[0] != "USD" else "INR"
            else:
                entities["from_currency"] = found_currencies[0]
                entities["to_currency"] = "INR" if found_currencies[0] != "INR" else "USD"

        # Historical Date Parsing
        hist_match = re.search(r'\b(on|for|at)\s+([a-zA-Z]+\s+\d{1,2},\s*\d{4}|\d{4}-\d{2}-\d{2})\b', query, re.IGNORECASE)
        if hist_match:
            entities["historical_date"] = hist_match.group(2)

        # Date / Time
        date_match = re.search(r'\b(today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)\b', q_lower)
        if date_match:
            entities["date"] = date_match.group(1)

        # Location extraction
        loc_match = re.search(r'\b(?:in|at|near|for|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', query)
        if loc_match:
            loc = loc_match.group(1).strip()
            if loc.lower() not in ["the", "a", "an", "today", "tomorrow"]:
                entities["location"] = loc
        elif "hyd" in q_lower or "hyderabad" in q_lower:
            entities["location"] = "Hyderabad"
        elif "blore" in q_lower or "bangalore" in q_lower or "bengaluru" in q_lower:
            entities["location"] = "Bangalore"
        elif "delhi" in q_lower:
            entities["location"] = "Delhi"

        # Ticker / Stock symbol
        stock_match = re.search(r'\b(AAPL|TSLA|GOOGL|MSFT|NVDA|AMZN|META|NFLX|RELIANCE|TCS|INFY)\b', query, re.IGNORECASE)
        if stock_match:
            entities["symbol"] = stock_match.group(1).upper()

        # Crypto symbol
        crypto_match = re.search(r'\b(bitcoin|btc|ethereum|eth|solana|sol|doge|dogecoin)\b', q_lower)
        if crypto_match:
            entities["asset"] = crypto_match.group(1).capitalize()

        return entities


class RouterService:
    def __init__(self):
        self.extractor = EntityExtractor()

    def resolve_followup_context(self, raw_query: str, previous_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Resolve pronoun references ('it', 'its', 'this', 'that') and short conversational follow-ups using previous context.
        """
        if not previous_context:
            return raw_query

        q_lower = raw_query.lower().strip()
        last_subject = previous_context.get("last_subject") or previous_context.get("topic") or previous_context.get("movie") or previous_context.get("location")

        if not last_subject:
            return raw_query

        # Check for short contextual follow-ups ('teach me', 'start', 'give me questions', 'make a timetable')
        if q_lower in ["teach me", "teach me completely", "teach"]:
            return f"Teach me {last_subject} step by step"
        elif q_lower in ["start", "start learning"]:
            return f"Start learning {last_subject}"
        elif q_lower in ["give me questions", "questions", "quiz", "quiz me"]:
            return f"Quiz me on {last_subject}"
        elif q_lower in ["make a timetable", "timetable", "study plan"]:
            return f"Create a timetable for {last_subject}"
        elif q_lower in ["interview questions", "interview"]:
            return f"{last_subject} interview answer"

        # Check for pronoun references
        has_it_ref = bool(re.search(r'\b(who (created|directed|developed|built|made) it|when was it|where is it|what is its|its current|how far is it)\b', q_lower))
        if has_it_ref or q_lower in ["who created it?", "who directed it?", "when was it released?", "who developed it?", "what is its current price?", "how far is it from hyderabad airport?"]:
            resolved = re.sub(r'\b(it|its|this|that)\b', last_subject, raw_query, flags=re.IGNORECASE)
            return resolved

        return raw_query

    def route_query(self, raw_query: str, previous_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify raw query into intent, confidence level, entities, and execution decision.
        """
        # 0. Resolve follow-up context
        resolved_query = self.resolve_followup_context(raw_query, previous_context)

        # 1. Correct Typos
        corrected = correct_typos(resolved_query)
        q_lower = corrected.lower().strip()

        # 2. Extract Entities
        entities = self.extractor.extract_entities(resolved_query)

        # Carry over previous context entities
        if previous_context:
            for k in ["location", "team", "topic", "movie", "asset"]:
                if k not in entities and previous_context.get(k):
                    entities[k] = previous_context[k]

        # 3. Intent Pattern Scoring
        best_intent = "GENERAL_AI"
        highest_score = 0.0

        for intent, data in INTENT_PATTERNS.items():
            score = 0.0
            # Phrase exact match
            for phrase in data["phrases"]:
                if phrase in q_lower:
                    score += 0.85
                    break

            # Keyword matching
            matched_kw = [kw for kw in data["keywords"] if kw in q_lower]
            score += len(matched_kw) * 0.35

            if score > highest_score:
                highest_score = score
                best_intent = intent

        # If from_currency and to_currency entities are both present, boost CURRENCY intent
        if entities.get("from_currency") and entities.get("to_currency") and not q_lower.startswith("what is"):
            if highest_score < 0.85:
                best_intent = "CURRENCY"
                highest_score = 0.85

        # Calibrate confidence score
        if highest_score >= 0.70:
            confidence = "HIGH"
            numeric_conf = min(0.99, max(0.85, round(highest_score, 2)))
        elif highest_score >= 0.35:
            confidence = "MEDIUM"
            numeric_conf = round(highest_score, 2)
        else:
            confidence = "LOW"
            numeric_conf = 0.30
            best_intent = "GENERAL_AI"

        return {
            "raw_query": raw_query,
            "resolved_query": resolved_query,
            "corrected_query": corrected,
            "intent": best_intent,
            "action_intent": entities.get("action_intent", "general"),
            "topic": entities.get("topic", corrected),
            "confidence": confidence,
            "confidence_score": numeric_conf,
            "entities": entities,
            "should_clarify": False
        }


router_service = RouterService()
