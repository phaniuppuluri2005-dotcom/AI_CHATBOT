"""
Automated Test Suite for Multi-Source Information Retrieval, Verification & Research Mode.
"""

from services.web_search_service import web_search_service
from services.router_service import router_service
from services.orchestrator import orchestrator
from utils.typo_tolerance import correct_typos


def test_query_decomposition():
    subqueries = web_search_service.decompose_query("Research Power BI and compare it with Tableau for data analyst jobs")
    assert len(subqueries) >= 2
    assert any("Power" in sq or "Tableau" in sq for sq in subqueries)


def test_source_deduplication_and_ranking():
    sample_sources = [
        {"title": "Python Docs", "url": "https://docs.python.org/3/", "source_name": "Python.org", "snippet": "Official python docs", "authority_rank": 1},
        {"title": "Duplicate Python Docs", "url": "https://docs.python.org/3/", "source_name": "Python.org", "snippet": "Official python docs", "authority_rank": 1},
        {"title": "Tech News", "url": "https://techcrunch.com/python-update", "source_name": "TechCrunch", "snippet": "Latest python updates", "authority_rank": 3},
        {"title": "Localhost Fake", "url": "http://localhost:8501/test", "source_name": "Local", "snippet": "Fake", "authority_rank": 5}
    ]
    ranked = web_search_service.deduplicate_and_rank_sources(sample_sources)
    assert len(ranked) == 2
    assert ranked[0]["source_name"] == "Python.org"
    assert not any("localhost" in s["url"] for s in ranked)


def test_typo_normalization_and_topic_extraction():
    assert "Python" in correct_typos("pythonn")
    assert "Python" in correct_typos("pyhton")
    assert "Power" in correct_typos("powr")
    assert "Tableau" in correct_typos("tablue")

    route = router_service.route_query("define pythonn")
    assert route["entities"].get("topic") == "Python"
    assert route["entities"].get("action_intent") == "define"


def test_research_routing_and_synthesis():
    route = router_service.route_query("Research the latest developments in Python 3.14")
    assert route["intent"] in ["RESEARCH", "CURRENT_INFO"]

    res = orchestrator.process_request("Research Python 3.14")
    assert "text_response" in res
    assert len(res["text_response"]) > 50
    assert "http://localhost" not in res["text_response"]
    assert "127.0.0.1" not in res["text_response"]


def test_followup_context_resolution():
    res1 = orchestrator.process_request("Tell me about Inception")
    ctx1 = res1.get("context", {})
    assert ctx1.get("last_subject") is not None

    route2 = router_service.route_query("Who directed it?", previous_context=ctx1)
    assert "Inception" in route2["resolved_query"]
