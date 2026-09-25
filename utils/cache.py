"""
In-Memory & Persistent Caching System for Phani AI.
Prevents duplicate API calls, reduces latency, and protects external API quotas.
"""

import time
import hashlib
import json
import logging
from typing import Any, Optional, Dict
from config.settings import settings

logger = logging.getLogger("PhaniAI.Cache")


class MemoryCache:
    def __init__(self, default_ttl: int = settings.CACHE_TTL_SECONDS):
        self._store: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def _generate_key(self, prefix: str, data: Any) -> str:
        raw = f"{prefix}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def get(self, prefix: str, key_data: Any) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None
        key = self._generate_key(prefix, key_data)
        item = self._store.get(key)
        if not item:
            return None
        if time.time() > item["expires_at"]:
            del self._store[key]
            return None
        logger.debug(f"Cache HIT for [{prefix}] {key_data}")
        return item["val"]

    def set(self, prefix: str, key_data: Any, value: Any, ttl: Optional[int] = None):
        if not settings.CACHE_ENABLED:
            return
        key = self._generate_key(prefix, key_data)
        effective_ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = {
            "val": value,
            "expires_at": time.time() + effective_ttl
        }
        logger.debug(f"Cache SET for [{prefix}] {key_data} (TTL: {effective_ttl}s)")

    def clear(self):
        self._store.clear()
        logger.info("Memory cache cleared.")


# Global cache instance
cache = MemoryCache()
