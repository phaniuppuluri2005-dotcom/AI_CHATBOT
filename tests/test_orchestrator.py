"""
Automated Test Suite for Phani AI Central Orchestrator & Multi-Intent Requests.
"""

from services.orchestrator import orchestrator


def test_multi_intent_detection():
    intents = orchestrator.detect_multi_intents("What is the weather in Hyderabad and show me Bitcoin price")
    assert "WEATHER" in intents or "CRYPTO" in intents
    assert len(intents) >= 1


def test_orchestrator_execution():
    res = orchestrator.process_request("What is the weather in Hyderabad and show me Bitcoin price")
    assert res["query"] is not None
    assert "WEATHER" in res["detected_intents"] or "CRYPTO" in res["detected_intents"]
    assert len(res["cards"]) >= 1
