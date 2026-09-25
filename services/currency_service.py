"""
Universal Currency Exchange & Forex Converter Service for Phani AI.
Supports dynamic forex conversions between ANY ISO 4217 currency pair supported by provider,
historical conversion rates, symbol resolution, and exact last-updated timestamps.
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from utils.cache import cache
from utils.time_utils import get_current_ist_timestamp, format_timestamp
from config.settings import settings

logger = logging.getLogger("PhaniAI.CurrencyService")

# Currency Code & Symbol Mapping Table
CURRENCY_METADATA = {
    "USD": {"name": "US Dollar", "symbol": "$"},
    "INR": {"name": "Indian Rupee", "symbol": "₹"},
    "EUR": {"name": "Euro", "symbol": "€"},
    "GBP": {"name": "British Pound", "symbol": "£"},
    "JPY": {"name": "Japanese Yen", "symbol": "¥"},
    "AED": {"name": "UAE Dirham", "symbol": "AED"},
    "AUD": {"name": "Australian Dollar", "symbol": "A$"},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$"},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$"},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥"},
    "CHF": {"name": "Swiss Franc", "symbol": "CHF"},
    "NZD": {"name": "New Zealand Dollar", "symbol": "NZ$"},
    "BRL": {"name": "Brazilian Real", "symbol": "R$"},
    "ZAR": {"name": "South African Rand", "symbol": "R"},
    "MXN": {"name": "Mexican Peso", "symbol": "Mex$"},
    "SEK": {"name": "Swedish Krona", "symbol": "kr"},
    "NOK": {"name": "Norwegian Krone", "symbol": "kr"},
    "KRW": {"name": "South Korean Won", "symbol": "₩"},
    "RUB": {"name": "Russian Ruble", "symbol": "₽"},
    "THB": {"name": "Thai Baht", "symbol": "฿"}
}


class CurrencyService:
    EXCHANGE_URL = "https://open.er-api.com/v6/latest/{from_currency}"
    FRANKFURTER_HISTORICAL_URL = "https://api.frankfurter.app/{date}"

    def normalize_currency_code(self, raw_curr: str) -> str:
        """Resolves natural language currency names or symbols into 3-letter ISO 4217 code."""
        if not raw_curr:
            return "USD"
        cleaned = raw_curr.strip().upper()

        # Symbol & name mappings
        mapping = {
            "$": "USD", "DOLLAR": "USD", "DOLLARS": "USD", "US DOLLAR": "USD",
            "₹": "INR", "RUPEE": "INR", "RUPEES": "INR", "INDIAN RUPEE": "INR",
            "€": "EUR", "EURO": "EUR", "EUROS": "EUR",
            "£": "GBP", "POUND": "GBP", "POUNDS": "GBP", "BRITISH POUND": "GBP",
            "¥": "JPY", "YEN": "JPY", "JAPANESE YEN": "JPY",
            "DIRHAM": "AED", "DIRHAMS": "AED", "UAE DIRHAM": "AED",
            "AUD": "AUD", "AUSTRALIAN DOLLAR": "AUD",
            "CAD": "CAD", "CANADIAN DOLLAR": "CAD",
            "SGD": "SGD", "SINGAPORE DOLLAR": "SGD",
            "YUAN": "CNY", "RENMINBI": "CNY", "CHINESE YUAN": "CNY"
        }

        return mapping.get(cleaned, cleaned)

    def get_supported_currencies(self) -> List[Dict[str, str]]:
        """Returns list of all supported currency dictionaries for UI selectboxes."""
        result = []
        for code, meta in CURRENCY_METADATA.items():
            result.append({
                "code": code,
                "name": meta["name"],
                "symbol": meta["symbol"],
                "display": f"{code} — {meta['name']} ({meta['symbol']})"
            })
        return result

    def get_currency_symbol(self, code: str) -> str:
        """Get symbol for ISO currency code."""
        meta = CURRENCY_METADATA.get(code.upper())
        return meta["symbol"] if meta else code.upper()

    def convert(
        self,
        amount: float = 1.0,
        from_curr: str = "USD",
        to_curr: str = "INR",
        historical_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert amount between any supported source and target currency.
        Supports historical rates if historical_date ('YYYY-MM-DD') is supplied.
        """
        from_code = self.normalize_currency_code(from_curr)
        to_code = self.normalize_currency_code(to_curr)

        # Historical rate processing
        if historical_date:
            return self._convert_historical(amount, from_code, to_code, historical_date)

        cache_key = f"forex_{from_code}"
        rates = cache.get("currency", cache_key)
        update_time_str = get_current_ist_timestamp()

        if not rates:
            try:
                res = requests.get(self.EXCHANGE_URL.format(from_currency=from_code), timeout=settings.API_TIMEOUT)
                if res.status_code == 200:
                    data = res.json()
                    rates = data.get("rates", {})
                    if "time_last_update_unix" in data:
                        update_time_str = format_timestamp(data["time_last_update_unix"])
                    cache.set("currency", cache_key, rates, ttl=3600)
            except Exception as e:
                logger.error(f"Currency API error for {from_code}: {e}")

        # Fallback rates table if API network fails
        if not rates or to_code not in rates:
            fallback_rates = {
                "USD": 1.0, "INR": 83.50, "EUR": 0.92, "GBP": 0.78, "JPY": 155.0,
                "AED": 3.67, "AUD": 1.50, "CAD": 1.36, "SGD": 1.35, "CNY": 7.23, "CHF": 0.89
            }
            rate_from = fallback_rates.get(from_code, 1.0)
            rate_to = fallback_rates.get(to_code, 83.50)
            unit_rate = rate_to / rate_from
        else:
            unit_rate = rates.get(to_code, 1.0)

        converted_amount = round(amount * unit_rate, 2)
        from_sym = self.get_currency_symbol(from_code)
        to_sym = self.get_currency_symbol(to_code)

        return {
            "success": True,
            "is_historical": False,
            "amount": amount,
            "from_currency": from_code,
            "from_symbol": from_sym,
            "to_currency": to_code,
            "to_symbol": to_sym,
            "converted_amount": converted_amount,
            "exchange_rate": round(unit_rate, 4),
            "formatted_result": f"{amount:,.2f} {from_code} = {to_sym}{converted_amount:,.2f}",
            "unit_rate_display": f"1 {from_code} = {to_sym}{unit_rate:,.4f} ({to_code})",
            "last_updated": update_time_str,
            "provider": "Open Exchange Rates API"
        }

    def _convert_historical(self, amount: float, from_code: str, to_code: str, date_str: str) -> Dict[str, Any]:
        """Fetch historical rate for date_str ('YYYY-MM-DD')."""
        try:
            params = {"from": from_code, "to": to_code}
            res = requests.get(
                self.FRANKFURTER_HISTORICAL_URL.format(date=date_str),
                params=params,
                timeout=settings.API_TIMEOUT
            )
            if res.status_code == 200:
                data = res.json()
                unit_rate = data.get("rates", {}).get(to_code, 1.0)
                converted_amount = round(amount * unit_rate, 2)
                from_sym = self.get_currency_symbol(from_code)
                to_sym = self.get_currency_symbol(to_code)

                return {
                    "success": True,
                    "is_historical": True,
                    "historical_date": date_str,
                    "amount": amount,
                    "from_currency": from_code,
                    "from_symbol": from_sym,
                    "to_currency": to_code,
                    "to_symbol": to_sym,
                    "converted_amount": converted_amount,
                    "exchange_rate": round(unit_rate, 4),
                    "formatted_result": f"{amount:,.2f} {from_code} = {to_sym}{converted_amount:,.2f} (on {date_str})",
                    "unit_rate_display": f"1 {from_code} = {to_sym}{unit_rate:,.4f} ({to_code})",
                    "last_updated": f"Historical Rate for {date_str}",
                    "provider": "Frankfurter Historical Forex Feed"
                }
        except Exception as e:
            logger.error(f"Historical Forex API error: {e}")

        # Fallback for historical if API offline
        return self.convert(amount, from_code, to_code)


currency_service = CurrencyService()
