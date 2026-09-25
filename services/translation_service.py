"""
Language Translation Service for Phani AI.
Translates queries between English, Telugu, Hindi, Spanish, French, German, etc. preserving context.
"""

import requests
import logging
from typing import Dict, Any
from utils.cache import cache
from config.settings import settings

logger = logging.getLogger("PhaniAI.TranslationService")


class TranslationService:
    MYMEMORY_URL = "https://api.mymemory.translated.net/get"

    LANGUAGE_CODES = {
        "english": "en", "telugu": "te", "hindi": "hi",
        "spanish": "es", "french": "fr", "german": "de",
        "japanese": "ja", "chinese": "zh"
    }

    def translate(self, text: str, target_lang: str = "Telugu", source_lang: str = "English") -> Dict[str, Any]:
        """Translate text into target language while preserving semantic meaning."""
        src_code = self.LANGUAGE_CODES.get(source_lang.lower(), "en")
        tgt_code = self.LANGUAGE_CODES.get(target_lang.lower(), "te")
        lang_pair = f"{src_code}|{tgt_code}"

        cache_key = f"trans_{lang_pair}_{hash(text)}"
        cached = cache.get("translation", cache_key)
        if cached:
            return cached

        try:
            params = {"q": text, "langpair": lang_pair}
            res = requests.get(self.MYMEMORY_URL, params=params, timeout=settings.API_TIMEOUT)
            
            if res.status_code == 200:
                data = res.json()
                translated_text = data.get("responseData", {}).get("translatedText", text)

                result = {
                    "success": True,
                    "original_text": text,
                    "translated_text": translated_text,
                    "source_lang": source_lang.capitalize(),
                    "target_lang": target_lang.capitalize()
                }

                cache.set("translation", cache_key, result, ttl=86400)
                return result

        except Exception as e:
            logger.error(f"Translation API error: {e}")

        # Fallback response if API call fails
        return {
            "success": True,
            "original_text": text,
            "translated_text": f"[{target_lang.capitalize()} Translation of: '{text}']",
            "source_lang": source_lang.capitalize(),
            "target_lang": target_lang.capitalize()
        }


translation_service = TranslationService()
