"""
Automated Unit Tests for Live Data Timestamp Requirement & Universal Currency Converter in Phani AI.
"""

from services.weather_service import weather_service
from services.crypto_service import crypto_service
from services.currency_service import currency_service
from services.cricket_service import cricket_service
from services.stock_service import stock_service
from services.news_service import news_service
from services.router_service import router_service
from services.orchestrator import orchestrator


def test_live_data_timestamps():
    """Verify that every live service returns a standardized timestamp."""
    # 1. Weather
    w_res = weather_service.get_weather("Hyderabad")
    assert "last_updated" in w_res, "Weather service missing last_updated"
    assert "IST" in w_res["last_updated"], f"Weather timestamp missing IST: {w_res['last_updated']}"
    assert "feels_like_c" in w_res, "Weather service missing feels_like_c"
    assert "humidity_pct" in w_res, "Weather service missing humidity_pct"

    # 2. Crypto
    cr_res = crypto_service.get_crypto_price("Bitcoin")
    assert "last_updated" in cr_res, "Crypto service missing last_updated"

    # 3. Cricket
    c_res = cricket_service.get_live_scores()
    assert "last_updated" in c_res, "Cricket service missing last_updated"
    assert "IST" in c_res["last_updated"], f"Cricket timestamp missing IST: {c_res['last_updated']}"

    # 4. Stock
    s_res = stock_service.get_stock_price("AAPL")
    assert "last_updated" in s_res, "Stock service missing last_updated"

    # 5. News
    n_res = news_service.get_news("technology")
    assert "last_updated" in n_res, "News service missing last_updated"

    # 6. Currency
    curr_res = currency_service.convert(100, "USD", "INR")
    assert "last_updated" in curr_res, "Currency service missing last_updated"


def test_universal_currency_converter():
    """Verify conversion across non-standard currency pairs and symbols."""
    # GBP to AED
    res1 = currency_service.convert(50, "GBP", "AED")
    assert res1["success"] is True
    assert res1["from_currency"] == "GBP"
    assert res1["to_currency"] == "AED"
    assert res1["converted_amount"] > 0

    # EUR to JPY
    res2 = currency_service.convert(100, "EUR", "JPY")
    assert res2["success"] is True
    assert res2["from_currency"] == "EUR"
    assert res2["to_currency"] == "JPY"

    # CAD to AUD
    res3 = currency_service.convert(200, "CAD", "AUD")
    assert res3["success"] is True
    assert res3["from_currency"] == "CAD"
    assert res3["to_currency"] == "AUD"


def test_currency_natural_language_routing():
    """Verify router extracts amounts and currency pairs accurately from natural language."""
    route1 = router_service.route_query("Convert 50 GBP into AED")
    assert route1["intent"] == "CURRENCY"
    assert route1["entities"].get("amount") == 50.0
    assert route1["entities"].get("from_currency") == "GBP"
    assert route1["entities"].get("to_currency") == "AED"

    route2 = router_service.route_query("100 EUR in JPY")
    assert route2["intent"] == "CURRENCY"
    assert route2["entities"].get("amount") == 100.0
    assert route2["entities"].get("from_currency") == "EUR"
    assert route2["entities"].get("to_currency") == "JPY"


def test_orchestrator_currency_live_response():
    """Verify orchestrator returns formatted live response with rate timestamp."""
    res = orchestrator.process_request("Convert 100 dollars to rupees")
    assert res["primary_intent"] == "CURRENCY"
    assert len(res["cards"]) > 0
    assert res["cards"][0]["type"] == "CURRENCY"
    assert "Rate updated:" in res["text_response"] or "Rate updated:" in res["cards"][0]["data"]["last_updated"] or "IST" in res["cards"][0]["data"]["last_updated"]
