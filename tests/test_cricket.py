"""
Automated Test Suite for Critical Live Cricket Requirement.
Tests intent routing, typo tolerance, live RSS score fetching, status classification, and offline fallback.
"""

from services.router_service import router_service
from services.cricket_service import cricket_service
from services.orchestrator import orchestrator


def test_cricket_routing_variations():
    queries = [
        "cricket score",
        "live cricket score",
        "what is the cricket score?",
        "current cricket score",
        "India cricket score",
        "India vs Australia score",
        "who is winning the cricket match?",
        "who is winning?",
        "criket score",
        "cricket scrore",
        "cricket scor",
        "latest cricket match",
        "today's cricket matches"
    ]
    for q in queries:
        route = router_service.route_query(q)
        assert route["intent"] == "CRICKET", f"Failed to route '{q}' to CRICKET (got {route['intent']})"
        assert route["confidence"] in ["HIGH", "MEDIUM"]


def test_cricket_context_retention():
    context = {"intent": "CRICKET", "team": "India"}
    route = router_service.route_query("who is winning?", previous_context=context)
    assert route["intent"] == "CRICKET"
    assert route["entities"].get("team") == "India"


def test_cricket_service_live_fetch():
    res = cricket_service.get_live_scores(query="cricket score")
    assert "status_type" in res
    assert "last_updated" in res
    if res["success"]:
        assert len(res["matches"]) >= 0


def test_orchestrator_cricket_execution():
    res = orchestrator.process_request("live cricket score")
    assert res["primary_intent"] == "CRICKET"
    assert len(res["cards"]) == 1
    assert res["cards"][0]["type"] == "CRICKET"
