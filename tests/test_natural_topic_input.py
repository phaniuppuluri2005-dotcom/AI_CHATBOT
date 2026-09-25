"""
Automated Test Suite for ChatGPT-Style Natural Topic Input & Response Generation in Phani AI.
"""

from services.router_service import router_service
from services.orchestrator import orchestrator
from services.ai_service import ai_service


def test_topic_only_queries_and_clean_entities():
    """Verify single-word/phrase topic queries extract clean entity without metadata leakage."""
    topics = [
        "Python", "SQL", "Machine Learning", "Physics", "Economics",
        "History", "Data Structures", "Power BI", "Java", "Cricket", "Photosynthesis"
    ]
    for top in topics:
        route = router_service.route_query(top)
        assert route["intent"] == "GENERAL_AI", f"Expected GENERAL_AI for '{top}', got {route['intent']}"
        assert route["entities"]["topic"].lower() == top.lower(), f"Expected clean topic '{top}', got '{route['entities']['topic']}'"
        assert route["entities"]["mode"] == "overview"
        assert route["entities"]["level"] is None


def test_explicit_instructions_override_defaults():
    """Verify explicit modifiers update level, detail, and mode parameters."""
    r1 = router_service.route_query("Python briefly")
    assert r1["entities"]["topic"] == "Python"
    assert r1["entities"]["detail"] == "brief"

    r2 = router_service.route_query("Explain Python at beginner level")
    assert r2["entities"]["topic"] == "Python"
    assert r2["entities"]["level"] == "beginner"

    r3 = router_service.route_query("Python interview answer")
    assert r3["entities"]["topic"] == "Python"
    assert r3["entities"]["mode"] == "interview"

    r4 = router_service.route_query("Python only code")
    assert r4["entities"]["topic"] == "Python"
    assert r4["entities"]["mode"] == "code"

    r5 = router_service.route_query("Quiz me on Python")
    assert r5["entities"]["topic"] == "Python"
    assert r5["entities"]["mode"] == "quiz"

    r6 = router_service.route_query("Teach me Python step by step")
    assert r6["entities"]["topic"] == "Python"
    assert r6["entities"]["mode"] == "learning"

    r7 = router_service.route_query("Create a timetable for Python")
    assert r7["entities"]["topic"] == "Python"
    assert r7["entities"]["mode"] == "timetable"


def test_contextual_followups():
    """Verify follow-up requests resolve topic context across turns."""
    res1 = orchestrator.process_request("Python")
    ctx1 = res1["context"]
    assert ctx1.get("topic") == "Python" or ctx1.get("last_subject") == "Python"

    res2 = orchestrator.process_request("Teach me", previous_context=ctx1)
    assert res2["entities"]["topic"] == "Python"
    assert res2["entities"]["mode"] == "learning"

    res3 = orchestrator.process_request("Give me questions", previous_context=ctx1)
    assert res3["entities"]["topic"] == "Python"
    assert res3["entities"]["mode"] == "quiz"

    res4 = orchestrator.process_request("Make a timetable", previous_context=ctx1)
    assert res4["entities"]["topic"] == "Python"
    assert res4["entities"]["mode"] == "timetable"


def test_no_generic_filler_in_response():
    """Verify AI responses contain real content and zero generic filler headers."""
    resp = ai_service._generate_fallback_response("Python")
    assert "core domain concept" not in resp.lower()
    assert "at a beginner level" not in resp.lower()
    assert "Python" in resp
    assert "Suggested Next Actions" in resp
