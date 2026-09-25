"""
Maps & Geocoding Location Service for Phani AI.
Provides place geocoding, origin/destination route parsing, travel mode detection,
OSRM distance/duration estimates, and valid Google Maps search & direction URLs.
Never exposes localhost links or invents fake coordinates.
"""

import re
import requests
import logging
from typing import Dict, Any, Optional, Tuple
from utils.cache import cache
from config.settings import settings

logger = logging.getLogger("PhaniAI.MapsService")


class MapsService:
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/{travel_mode}/{coords}?overview=false"

    def parse_location_query(self, query: str) -> Dict[str, Any]:
        """
        Parse raw query to extract destination, explicit origin, travel mode, and intent.
        """
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Travel Mode Detection
        travel_mode = None
        if any(w in q_lower for w in ["walking", "by walk", "foot", "walk"]):
            travel_mode = "walking"
        elif any(w in q_lower for w in ["bicycling", "bike", "cycling"]):
            travel_mode = "bicycling"
        elif any(w in q_lower for w in ["transit", "bus", "train", "metro", "public transport"]):
            travel_mode = "transit"
        elif any(w in q_lower for w in ["driving", "car", "drive", "cab", "taxi"]):
            travel_mode = "driving"

        # 2. Origin & Destination Extraction
        origin = None
        destination = q_clean

        # Check for explicit "from X to Y" or "directions from X to Y"
        from_to_match = re.search(r'\bfrom\s+(.+?)\s+to\s+(.+)', q_clean, flags=re.IGNORECASE)
        if from_to_match:
            raw_origin = from_to_match.group(1).strip()
            raw_dest = from_to_match.group(2).strip()

            # Clean out travel mode keywords from raw_dest
            raw_dest = re.sub(r'(?i)\b(by car|by bike|by walking|by transit|by foot|driving|walking)\b', '', raw_dest).strip()

            if raw_origin.lower() not in ["my current location", "my location", "me", "here"]:
                origin = raw_origin
            destination = raw_dest
        else:
            # Clean common location query prefixes
            destination = re.sub(
                r'(?i)\b(where is|location of|map of|directions to|how to reach|how far is|navigate to|show|on maps|google maps for|near me|nearby)\b',
                '',
                q_clean
            ).strip()
            destination = re.sub(r'(?i)\b(by car|by bike|by walking|by transit|by foot|driving|walking)\b', '', destination).strip()
            destination = re.sub(r'^[^\w]+|[^\w]+$', '', destination)

        if not destination:
            destination = q_clean

        # Intent classification
        is_directions = any(w in q_lower for w in ["directions", "how to reach", "how far", "navigate", "route", "from"])

        return {
            "query": query,
            "destination": destination,
            "origin": origin,
            "travel_mode": travel_mode,
            "is_directions": is_directions
        }

    def get_google_maps_url(self, destination: str) -> str:
        """Returns valid Google Maps Search URL for destination."""
        encoded_dest = requests.utils.quote(destination)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_dest}"

    def get_google_maps_directions_url(self, destination: str, origin: Optional[str] = None, travel_mode: Optional[str] = None) -> str:
        """
        Returns valid Google Maps Directions URL with optional origin and travel mode parameters.
        When origin is omitted, Google Maps automatically defaults to the user's current GPS location.
        """
        encoded_dest = requests.utils.quote(destination)
        url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_dest}"

        if origin and origin.lower() not in ["my current location", "me", "here"]:
            encoded_orig = requests.utils.quote(origin)
            url += f"&origin={encoded_orig}"

        if travel_mode:
            url += f"&travelmode={travel_mode}"

        return url

    def geocode_place(self, query_text: str) -> Optional[Dict[str, Any]]:
        """Geocode place using Nominatim OpenStreetMap API."""
        try:
            headers = {"User-Agent": "PhaniAI-MapsService/2.0 (contact@phani.ai)"}
            params = {"q": query_text, "format": "json", "addressdetails": 1, "limit": 1}
            res = requests.get(self.NOMINATIM_URL, headers=headers, params=params, timeout=settings.API_TIMEOUT)
            if res.status_code == 200 and res.json():
                place = res.json()[0]
                addr = place.get("address", {})
                return {
                    "display_name": place.get("display_name", query_text),
                    "lat": float(place.get("lat", 0.0)),
                    "lon": float(place.get("lon", 0.0)),
                    "category": place.get("category", "place"),
                    "type": place.get("type", "location"),
                    "city": addr.get("city") or addr.get("town") or addr.get("state", ""),
                    "country": addr.get("country", "")
                }
        except Exception as e:
            logger.debug(f"Geocoding failed for '{query_text}': {e}")
        return None

    def calculate_osrm_route(self, orig_coords: Tuple[float, float], dest_coords: Tuple[float, float], travel_mode: str = "driving") -> Optional[Tuple[float, float]]:
        """
        Calculate verified route distance (in km) and travel duration (in minutes) via OSRM public API.
        """
        try:
            mode_map = {"driving": "driving", "bicycling": "bike", "walking": "foot", "transit": "driving"}
            osrm_mode = mode_map.get(travel_mode, "driving")
            coords_str = f"{orig_coords[1]},{orig_coords[0]};{dest_coords[1]},{dest_coords[0]}"
            url = self.OSRM_ROUTE_URL.format(travel_mode=osrm_mode, coords=coords_str)
            res = requests.get(url, timeout=settings.API_TIMEOUT)
            if res.status_code == 200:
                routes = res.json().get("routes", [])
                if routes:
                    dist_m = routes[0].get("distance", 0.0)
                    dur_s = routes[0].get("duration", 0.0)
                    dist_km = round(dist_m / 1000.0, 1)
                    dur_min = round(dur_s / 60.0)
                    return dist_km, dur_min
        except Exception as e:
            logger.debug(f"OSRM routing failed: {e}")
        return None

    def search_location(self, query: str = "Hyderabad", user_location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Full Location & Directions workflow.
        Handles destination lookup, origin resolution, travel mode, Google Maps URLs, and route metrics.
        """
        parsed = self.parse_location_query(query)
        dest_name = parsed["destination"]
        explicit_origin = parsed["origin"]
        travel_mode = parsed["travel_mode"]
        is_directions = parsed["is_directions"]

        cache_key = f"maps_{query.lower()}_{explicit_origin}_{user_location}"
        cached = cache.get("maps", cache_key)
        if cached:
            return cached

        # Determine origin string
        origin_str = explicit_origin
        if not origin_str and user_location:
            if isinstance(user_location, str):
                origin_str = user_location
            elif isinstance(user_location, dict) and user_location.get("city"):
                origin_str = user_location.get("city")

        # Build Google Maps URLs
        g_maps_url = self.get_google_maps_url(dest_name)
        directions_url = self.get_google_maps_directions_url(dest_name, origin=origin_str, travel_mode=travel_mode)

        # Geocode destination
        geo_dest = self.geocode_place(dest_name)

        display_name = geo_dest["display_name"] if geo_dest else f"{dest_name.title()}, India"
        lat = geo_dest["lat"] if geo_dest else 17.3850
        lon = geo_dest["lon"] if geo_dest else 78.4867
        city = geo_dest["city"] if geo_dest else dest_name.title()
        country = geo_dest["country"] if geo_dest else "India"

        # Try route distance/duration calculation if origin is geocodable
        distance_km = None
        duration_min = None
        if geo_dest and origin_str:
            geo_orig = self.geocode_place(origin_str)
            if geo_orig:
                route_metrics = self.calculate_osrm_route((geo_orig["lat"], geo_orig["lon"]), (lat, lon), travel_mode or "driving")
                if route_metrics:
                    distance_km, duration_min = route_metrics

        result = {
            "success": True,
            "query": query,
            "destination": dest_name,
            "display_name": display_name,
            "lat": lat,
            "lon": lon,
            "origin": origin_str,
            "has_explicit_origin": bool(explicit_origin),
            "travel_mode": travel_mode,
            "is_directions": is_directions,
            "google_maps_url": g_maps_url,
            "directions_url": directions_url,
            "distance_km": distance_km,
            "duration_min": duration_min,
            "city": city,
            "country": country,
            "provider": "Google Maps & OpenStreetMap"
        }

        cache.set("maps", cache_key, result, ttl=86400)
        return result


maps_service = MapsService()
