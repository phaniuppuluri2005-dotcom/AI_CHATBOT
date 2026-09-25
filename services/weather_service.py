"""
Weather & Climate Forecast Service for Phani AI.
Utilizes Open-Meteo free API for live temperature, condition, feels-like temp, humidity, wind, rain, and forecasts.
Provides exact last-updated date, local time, and timezone.
"""

import requests
import logging
from typing import Dict, Any, Optional
from utils.cache import cache
from utils.time_utils import get_current_ist_timestamp, format_timestamp
from config.settings import settings

logger = logging.getLogger("PhaniAI.WeatherService")


class WeatherService:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, location: str = "Hyderabad") -> Dict[str, Any]:
        """Fetch current weather, feels-like temp, humidity, wind, rain, and forecast for location."""
        cache_key = f"weather_{location.lower()}"
        cached = cache.get("weather", cache_key)
        if cached:
            return cached

        try:
            # 1. Geocode location name to latitude & longitude
            geo_res = requests.get(
                self.GEOCODING_URL,
                params={"name": location, "count": 1, "language": "en", "format": "json"},
                timeout=settings.API_TIMEOUT
            )
            geo_data = geo_res.json()

            if not geo_data.get("results"):
                return {
                    "success": False,
                    "location": location,
                    "error": f"Location '{location}' not found. Please specify a valid city name.",
                    "last_updated": get_current_ist_timestamp()
                }

            city_info = geo_data["results"][0]
            lat = city_info["latitude"]
            lon = city_info["longitude"]
            city_name = city_info.get("name", location)
            country = city_info.get("country", "")

            # 2. Fetch current weather & daily forecast
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "hourly": "temperature_2m,relativehumidity_2m,apparent_temperature,precipitation_probability",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto"
            }
            w_res = requests.get(self.WEATHER_URL, params=params, timeout=settings.API_TIMEOUT)
            w_data = w_res.json()

            current = w_data.get("current_weather", {})
            temp = current.get("temperature", 28.0)
            windspeed = current.get("windspeed", 12.0)
            weathercode = current.get("weathercode", 0)

            # Extract humidity and feels-like temp from hourly data if available
            hourly = w_data.get("hourly", {})
            humidity_list = hourly.get("relativehumidity_2m", [70])
            feels_list = hourly.get("apparent_temperature", [temp + 2])
            
            humidity_pct = humidity_list[0] if humidity_list else 70
            feels_like_c = feels_list[0] if feels_list else round(temp + 1.5, 1)

            # Weather code interpretation
            condition = "Clear / Sunny"
            if weathercode in [1, 2, 3]:
                condition = "Partly Cloudy"
            elif weathercode in [45, 48]:
                condition = "Foggy"
            elif weathercode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                condition = "Rainy / Showers"
            elif weathercode in [95, 96, 99]:
                condition = "Thunderstorm"

            daily = w_data.get("daily", {})
            max_temp = daily.get("temperature_2m_max", [temp])[0]
            min_temp = daily.get("temperature_2m_min", [temp])[0]
            rain_sum = daily.get("precipitation_sum", [0.0])[0]

            last_updated_time = get_current_ist_timestamp()
            if "time" in current:
                last_updated_time = format_timestamp(current["time"])

            result = {
                "success": True,
                "location": f"{city_name}, {country}".strip(", "),
                "temperature_c": temp,
                "feels_like_c": feels_like_c,
                "humidity_pct": humidity_pct,
                "condition": condition,
                "temp_max_c": max_temp,
                "temp_min_c": min_temp,
                "wind_speed_kmh": windspeed,
                "rain_prob_mm": rain_sum,
                "will_rain": condition.startswith("Rainy") or rain_sum > 0.5,
                "umbrella_needed": condition.startswith("Rainy") or rain_sum > 0.5,
                "last_updated": last_updated_time,
                "provider": "Open-Meteo Weather Service"
            }

            cache.set("weather", cache_key, result, ttl=900)
            return result

        except Exception as e:
            logger.error(f"Weather API error for {location}: {e}")
            return {
                "success": False,
                "location": location,
                "error": "Weather service is currently unavailable. Please try again shortly.",
                "last_updated": get_current_ist_timestamp()
            }


weather_service = WeatherService()
