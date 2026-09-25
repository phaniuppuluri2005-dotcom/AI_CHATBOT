"""
Automated Test Suite for Movie Search Multi-Matching, Year Filtering, and Dictionary Removal.
"""

from services.router_service import router_service
from services.movies_service import movies_service
from services.orchestrator import orchestrator


def test_general_ai_routing_no_dictionary():
    """Verify normal knowledge questions route to GENERAL_AI, never to dictionary."""
    general_queries = [
        "Python",
        "What is Python?",
        "SQL",
        "Power BI",
        "What is a stack?",
        "What is machine learning?",
        "What is Bitcoin?",
        "What is weather?",
        "What is cricket?",
        "What is USD?",
        "What is a CSV?"
    ]
    for q in general_queries:
        route = router_service.route_query(q)
        assert route["intent"] == "GENERAL_AI", f"Expected GENERAL_AI for '{q}', got {route['intent']}"


def test_specialized_services_routing_boundaries():
    """Verify specialized services trigger ONLY when intent actually requires live data/tools."""
    assert router_service.route_query("Current Bitcoin price")["intent"] == "CRYPTO"
    assert router_service.route_query("Weather in Hyderabad right now")["intent"] == "WEATHER"
    assert router_service.route_query("Current cricket score")["intent"] == "CRICKET"
    assert router_service.route_query("Convert 100 USD to INR")["intent"] == "CURRENCY"
    assert router_service.route_query("Where is Charminar?")["intent"] == "MAPS"
    assert router_service.route_query("Tell me about Inception")["intent"] == "MOVIES"


def test_movie_typo_abbreviation_and_year_filtering():
    """Verify typo tolerance, abbreviations (OG, Puspha), and parenthesized year filtering in movies."""
    # 1. Parenthesized year 'They Call Him OG (2025)' & 'pushpa (2024)'
    res_og_paren = movies_service.search_movie("They Call Him OG (2025)")
    assert res_og_paren["success"] is True
    assert res_og_paren["movies"][0]["imdb_id"] == "tt24060892" or "OG" in res_og_paren["movies"][0]["title"].upper()

    res_pushpa_paren = movies_service.search_movie("pushpa (2024)")
    assert res_pushpa_paren["success"] is True
    assert res_pushpa_paren["movies"][0]["year"] == "2024"

    # 2. Standalone year 'They Call Him OG 2025' & 'pushpa 2021'
    res_og_standalone = movies_service.search_movie("They Call Him OG 2025")
    assert res_og_standalone["success"] is True
    assert res_og_standalone["movies"][0]["imdb_id"] == "tt24060892" or "OG" in res_og_standalone["movies"][0]["title"].upper()

    res2 = movies_service.search_movie("pushpa 2021")
    assert res2["success"] is True
    assert res2["movies"][0]["year"] == "2021"

    # 3. Typo 'puspha'
    res1 = movies_service.search_movie("puspha")
    assert res1["success"] is True
    assert any("Pushpa" in m["title"] for m in res1["movies"])

    # 4. Abbreviation 'og' or 'og (2025)'
    res3 = movies_service.search_movie("og (2025)")
    assert res3["success"] is True
    assert any("OG" in m["title"].upper() or "O.G." in m["title"].upper() for m in res3["movies"])

    # 5. Multi-match 'Batman', 'Avatar', 'Inception'
    for movie_name in ["Batman", "Avatar", "Inception"]:
        res_m = movies_service.search_movie(movie_name)
        assert res_m["success"] is True
        assert len(res_m["movies"]) >= 1


def test_movie_nonexistent_and_error_handling():
    """Verify clean error message for non-existent movie without KeyError or dictionary fallback."""
    res = movies_service.search_movie("randommoviexyz123")
    assert res["success"] is False
    assert "No verified movie match was found" in res["error"]
    assert res["movies"] == []
    assert res["count"] == 0


def test_movie_followup_context():
    """Verify movie follow-up questions preserve movie context across turns."""
    res1 = orchestrator.process_request("They Call Him OG")
    ctx1 = res1.get("context", {})
    assert ctx1.get("movie") is not None or ctx1.get("last_subject") is not None

    res2 = orchestrator.process_request("Who directed it?", previous_context=ctx1)
    assert res2["primary_intent"] in ["MOVIES", "GENERAL_AI"]
    assert "OG" in res2["text_response"] or "Director" in res2["text_response"] or "directed" in res2["text_response"].lower()
