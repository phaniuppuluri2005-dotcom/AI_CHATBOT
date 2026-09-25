"""
Cryptocurrency Live Market Service for Phani AI.
Fetches crypto prices, 24h percentage changes, market cap, and volume using CoinGecko API.
Ensures exact live timestamps (e.g. '24 Sep 2026, 9:35 PM IST') and clear failure messages.
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from utils.cache import cache
from utils.time_utils import get_current_ist_timestamp, format_timestamp
from config.settings import settings

logger = logging.getLogger("PhaniAI.CryptoService")


class CryptoService:
    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
    MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"

    def get_crypto_price(self, asset: str = "Bitcoin") -> Dict[str, Any]:
        """Fetch cryptocurrency price, 24h stats, market info, and exact timestamp."""
        asset_clean = asset.lower().strip()
        id_map = {
            "bitcoin": "bitcoin", "btc": "bitcoin",
            "ethereum": "ethereum", "eth": "ethereum",
            "solana": "solana", "sol": "solana",
            "dogecoin": "dogecoin", "doge": "dogecoin",
            "cardano": "cardano", "ada": "cardano",
            "ripple": "ripple", "xrp": "ripple"
        }
        crypto_id = id_map.get(asset_clean, "bitcoin")

        cache_key = f"crypto_{crypto_id}"
        cached = cache.get("crypto", cache_key)
        if cached:
            return cached

        last_updated_time = get_current_ist_timestamp()

        try:
            params = {
                "ids": crypto_id,
                "vs_currencies": "usd,inr",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true",
                "include_last_updated_at": "true"
            }
            res = requests.get(self.COINGECKO_URL, params=params, timeout=settings.API_TIMEOUT)
            
            if res.status_code == 200:
                data = res.json().get(crypto_id, {})
                if data:
                    price_usd = data.get("usd", 0.0)
                    price_inr = data.get("inr", 0.0)
                    change_24h_pct = round(data.get("usd_24h_change", 0.0), 2)
                    market_cap_usd = data.get("usd_market_cap", 0.0)
                    vol_24h_usd = data.get("usd_24h_vol", 0.0)
                    
                    if "last_updated_at" in data:
                        last_updated_time = format_timestamp(data["last_updated_at"])

                    change_24h_val_inr = round(price_inr * (change_24h_pct / 100.0), 2)

                    result = {
                        "success": True,
                        "asset": crypto_id.capitalize(),
                        "symbol": crypto_id[:3].upper() if crypto_id != "bitcoin" else "BTC",
                        "price_usd": f"${price_usd:,.2f}",
                        "price_inr": f"₹{price_inr:,.2f}",
                        "change_24h_pct": change_24h_pct,
                        "change_24h_inr": f"₹{change_24h_val_inr:,.2f}",
                        "is_positive": change_24h_pct >= 0,
                        "market_cap_usd": f"${market_cap_usd:,.0f}",
                        "volume_24h_usd": f"${vol_24h_usd:,.0f}",
                        "last_updated": last_updated_time,
                        "provider": "CoinGecko Live Crypto Feed"
                    }

                    cache.set("crypto", cache_key, result, ttl=180)
                    return result

        except Exception as e:
            logger.error(f"Crypto API error for {asset}: {e}")

        # Explicit failure message when live crypto feed is unavailable
        return {
            "success": False,
            "asset": crypto_id.capitalize(),
            "error": f"Live {crypto_id.capitalize()} data is currently unavailable.",
            "last_updated": get_current_ist_timestamp(),
            "provider": "CoinGecko Live Crypto Feed"
        }


crypto_service = CryptoService()
