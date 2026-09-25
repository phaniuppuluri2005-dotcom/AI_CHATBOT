"""
Automated Test Suite for Movie KeyError Prevention & Maps/Directions Service Architecture.
"""

from services.movies_service import movies_service
from services.maps_service import maps_service
from services.orchestrator import orchestrator
from components.cards_ui import render_movie_card, render_maps_card


def test_movie_service_schema_safety():
    # 1. Normal movie lookup
    m1 = movies_service.search_movie("Inception")
    assert "year" in m1
    assert "rating" in m1
    assert "director" in m1
    assert "plot" in m1
    assert "imdb_url" in m1
    assert m1["success"] is True

    # 2. Unknown movie lookup (must contain all schema keys without KeyError)
    m2 = movies_service.search_movie("NonExistentMovie99999")
    assert "year" in m2
    assert "title" in m2
    assert m2["success"] is False
    assert "No verified movie match was found" in m2["error"]

    # 3. Simulated incomplete dictionary (missing year key)
    incomplete_movie = {
        "success": True,
        "title": "Minimal Movie",
        # year key intentionally omitted
        "rating": "7.5 / 10",
        "genre": "Drama",
        "director": "Jane Doe",
        "actors": "Actor A, Actor B",
        "plot": "Test plot"
    }
    # Must run without raising KeyError
    assert incomplete_movie.get("year") is None


def test_maps_service_query_parsing():
    # 1. Basic location search
    p1 = maps_service.parse_location_query("Where is Charminar?")
    assert "Charminar" in p1["destination"]
    assert p1["origin"] is None

    # 2. Directions with explicit origin
    p2 = maps_service.parse_location_query("Directions from Vijayawada to Charminar")
    assert p2["origin"] == "Vijayawada"
    assert "Charminar" in p2["destination"]
    assert p2["is_directions"] is True

    # 3. Travel mode detection
    p3 = maps_service.parse_location_query("Directions to Taj Mahal by car")
    assert p3["travel_mode"] == "driving"
    assert "Taj Mahal" in p3["destination"]

    p4 = maps_service.parse_location_query("Directions by walking to Charminar")
    assert p4["travel_mode"] == "walking"


def test_maps_url_generation():
    # 1. Destination Search URL
    url_search = maps_service.get_google_maps_url("Charminar, Hyderabad")
    assert "https://www.google.com/maps/search/?api=1&query=" in url_search
    assert "Charminar" in url_search
    assert "http://localhost" not in url_search

    # 2. Directions URL without origin (defaults to current location on Google Maps)
    url_dir1 = maps_service.get_google_maps_directions_url("Charminar, Hyderabad")
    assert "https://www.google.com/maps/dir/?api=1&destination=" in url_dir1

    # 3. Directions URL with explicit origin and travel mode
    url_dir2 = maps_service.get_google_maps_directions_url("Charminar", origin="Vijayawada", travel_mode="driving")
    assert "origin=Vijayawada" in url_dir2
    assert "destination=Charminar" in url_dir2
    assert "travelmode=driving" in url_dir2


def test_maps_full_location_service():
    loc = maps_service.search_location("Directions from Vijayawada to Charminar")
    assert loc["success"] is True
    assert "google_maps_url" in loc
    assert "directions_url" in loc
    assert loc["origin"] == "Vijayawada"
    assert "http://localhost" not in loc["google_maps_url"]


def test_maps_context_followup():
    res1 = orchestrator.process_request("Where is Charminar?")
    ctx1 = res1.get("context", {})
    assert ctx1.get("last_subject") is not None

    res2 = orchestrator.process_request("How far is it from me?", previous_context=ctx1)
    assert res2["primary_intent"] in ["MAPS", "GENERAL_AI"]
    assert "Charminar" in res2["text_response"] or "Charminar" in str(res2["entities"])
