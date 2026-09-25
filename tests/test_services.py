"""
Automated Test Suite for Phani AI Real-Time Services & Tools.
"""

from services.weather_service import weather_service
from services.crypto_service import crypto_service
from services.currency_service import currency_service
from services.wikipedia_service import wikipedia_service


def test_weather_service():
    res = weather_service.get_weather("Hyderabad")
    assert res["success"] is True
    assert "Hyderabad" in res["location"]
    assert "temperature_c" in res


def test_crypto_service():
    res = crypto_service.get_crypto_price("Bitcoin")
    assert res["success"] is True
    assert res["asset"] == "Bitcoin"
    assert "price_usd" in res


def test_currency_service():
    res = currency_service.convert(100.0, "USD", "INR")
    assert res["success"] is True
    assert res["amount"] == 100.0
    assert res["converted_amount"] > 0.0


def test_wikipedia_service():
    res = wikipedia_service.get_summary("Artificial Intelligence")
    assert res["success"] is True
    assert "artificial intelligence" in res["title"].lower()
