"""
Automated Test Suite for Phani AI Query Router, Typo Tolerance, and Entity Extraction.
"""

from services.router_service import router_service
from utils.typo_tolerance import correct_typos, similarity_ratio


def test_typo_correction():
    assert "weather" in correct_typos("wether").lower()
    assert "cricket" in correct_typos("criket").lower()
    assert "bitcoin" in correct_typos("bitcion").lower()
    assert "hyderabad" in correct_typos("hyd").lower()


def test_weather_routing():
    queries = [
        "What is the weather in Hyderabad?",
        "wether in Hyderabad",
        "what's temp in hyd",
        "will it rain in Hyderabad tomorrow"
    ]
    for q in queries:
        route = router_service.route_query(q)
        assert route["intent"] == "WEATHER", f"Failed to map '{q}' to WEATHER (got {route['intent']})"
        assert route["confidence"] in ["HIGH", "MEDIUM"]


def test_cricket_routing():
    queries = [
        "Who won today's cricket match?",
        "criket score today",
        "live cricket score"
    ]
    for q in queries:
        route = router_service.route_query(q)
        assert route["intent"] == "CRICKET", f"Failed to map '{q}' to CRICKET (got {route['intent']})"


def test_crypto_routing():
    route = router_service.route_query("bitcion price")
    assert route["intent"] == "CRYPTO"
    assert route["entities"].get("asset") == "Bitcoin"


def test_currency_routing():
    route = router_service.route_query("Convert 500 dollars to rupees")
    assert route["intent"] == "CURRENCY"
    assert route["entities"].get("amount") == 500.0
