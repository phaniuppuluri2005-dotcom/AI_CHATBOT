"""
Automated Test Suite for Universal Topic Explanation System.
Tests natural-language parsing, dynamic topic explanation across diverse domains, dynamic quiz generation, and timetables.
"""

from services.student_service import student_service


def test_natural_language_topic_parsing():
    parsed = student_service.parse_topic_request("Explain quantum computing briefly for a beginner with an example")
    assert "Quantum" in parsed["topic"]
    assert parsed["length"] == "brief"
    assert parsed["level"] == "beginner"
    assert parsed["include_example"] is True


def test_dynamic_explanation_diverse_domains():
    domains = [
        "Quantum Mechanics",
        "Photosynthesis",
        "Indian Constitution",
        "Inflation in Economics",
        "Fourier Transform",
        "How Airplanes Fly",
        "Philosophy of Ethics"
    ]
    for dom in domains:
        exp = student_service.explain_topic(dom, target_level="beginner", length_style="brief")
        assert exp is not None
        assert len(exp) > 50


def test_dynamic_quiz_generation():
    quizzes, count = student_service.generate_dynamic_quiz_by_query("give me 10 questions about physics")
    assert isinstance(quizzes, list)
    assert count == 10
    assert len(quizzes) == 10
    assert "question" in quizzes[0]


def test_study_timetable_generation():
    plan = student_service.generate_study_timetable("Create a 30-day Python study plan")
    assert "Study Plan" in plan or "Timetable" in plan
    assert len(plan) > 50
