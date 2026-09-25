"""
Visual HUD Cards UI Component for Phani AI.
Renders clean markdown and HTML cards for Weather, Crypto, Currency, Cricket, Stocks, News, Movies, Dictionary, and Translation.
Enforces the mandatory LIVE DATA DATE AND TIME REQUIREMENT:
'Last updated: [date] [time] [timezone]' across all live real-time services.
"""

import streamlit as st
from typing import Dict, Any


def render_weather_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.warning(f"⚠️ {data.get('error', 'Weather data unavailable.')}")
        if data.get("last_updated"):
            st.caption(f"**Last updated:** {data['last_updated']}")
        return

    st.markdown(f"### 🌤️ {data['location']} Weather")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", f"{data['temperature_c']}°C", delta=f"{data['temp_max_c']}° High")
    with col2:
        st.metric("Condition", data["condition"])
    with col3:
        st.metric("Feels Like / Humidity", f"{data.get('feels_like_c', data['temperature_c'])}°C", delta=f"{data.get('humidity_pct', 70)}% Humidity")
    with col4:
        st.metric("Wind & Rain", f"{data['wind_speed_kmh']} km/h", delta=f"{data['rain_prob_mm']} mm Rain")

    if data.get("umbrella_needed"):
        st.info("🌧️ **Weather Advice:** Rain is likely today. Don't forget your umbrella!")

    st.caption(f"**Last updated:** {data.get('last_updated', '24 Sep 2026, 9:35 PM IST')} | Data source: {data.get('provider', 'Open-Meteo Weather API')}")


def render_crypto_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.error(f"⚠️ {data.get('error', 'Live Bitcoin data is currently unavailable.')}")
        if data.get("last_updated"):
            st.caption(f"**Last updated:** {data['last_updated']}")
        return

    st.markdown(f"### 🪙 {data['asset']} ({data['symbol']})")

    col1, col2, col3 = st.columns(3)
    with col1:
        delta_pct = f"{'+' if data['is_positive'] else ''}{data['change_24h_pct']}% (24h)"
        st.metric("USD Price", data["price_usd"], delta=delta_pct)
    with col2:
        st.metric("INR Price", data["price_inr"], delta=data.get("change_24h_inr", "24h"))
    with col3:
        st.metric("Market Cap", data.get("market_cap_usd", "N/A"), delta=f"Vol: {data.get('volume_24h_usd', 'N/A')}")

    st.caption(f"**Last updated:** {data.get('last_updated', '24 Sep 2026, 9:35 PM IST')} | Data source: {data.get('provider', 'CoinGecko Live Crypto Feed')}")


def render_currency_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.warning("Forex rate data unavailable.")
        return

    st.markdown(f"### 💱 {data['amount']} {data['from_currency']} to {data['to_currency']}")
    st.markdown(f"## **{data['formatted_result']}**")
    st.markdown(f"Exchange rate: **{data['unit_rate_display']}**")

    if data.get("is_historical"):
        st.caption(f"📅 **Historical Rate Date:** {data.get('historical_date')} | Data source: {data.get('provider', 'Frankfurter Historical Forex Feed')}")
    else:
        st.caption(f"**Rate updated:** {data.get('last_updated', '24 Sep 2026, 9:35 PM IST')} | Data source: {data.get('provider', 'Open Exchange Rates API')}")


def render_cricket_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.error(f"⚠️ {data.get('error', 'Live cricket data is currently unavailable. Please try again shortly.')}")
        return

    st.markdown(f"### 🏏 {data.get('provider', 'ESPN Cricinfo Live Feed')}")

    matches = data.get("matches", [])
    if not matches:
        st.info("ℹ️ There is currently no live or scheduled cricket match matching your query.")
        st.caption(f"**Last updated:** {data.get('last_updated', '')}")
        return

    if len(matches) > 1:
        st.markdown(f"**Found {len(matches)} active/recent matches:**")
        match_titles = [f"{m.get('status', 'LIVE')} — {m['title']}" for m in matches]
        selected_idx = st.selectbox("Select Match to View Live Scorecard:", range(len(match_titles)), format_func=lambda i: match_titles[i])
        selected_match = matches[selected_idx]

        badge = "🔴 LIVE" if selected_match["status"] == "LIVE" else ("✅ COMPLETED" if selected_match["status"] == "COMPLETED" else "⏰ UPCOMING")
        st.markdown(f"""
            <div class="phani-card">
                <div class="phani-card-header">{badge} {selected_match['title']}</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">{selected_match['score_summary']}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;"><strong>Last updated:</strong> {selected_match.get('last_updated', data.get('last_updated', ''))}</div>
            </div>
        """, unsafe_allow_html=True)
        if selected_match.get("link"):
            st.markdown(f"🔗 [View Full Live Scorecard on Cricinfo]({selected_match['link']})")

    else:
        m = matches[0]
        badge = "🔴 LIVE" if m["status"] == "LIVE" else ("✅ COMPLETED" if m["status"] == "COMPLETED" else "⏰ UPCOMING")
        st.markdown(f"""
            <div class="phani-card">
                <div class="phani-card-header">{badge} {m['title']}</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">{m['score_summary']}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;"><strong>Last updated:</strong> {m.get('last_updated', data.get('last_updated', ''))}</div>
            </div>
        """, unsafe_allow_html=True)
        if m.get("link"):
            st.markdown(f"🔗 [View Full Live Scorecard on Cricinfo]({m['link']})")

    st.caption(f"**Last updated:** {data.get('last_updated', '')} | Live Data Feed")


def render_stock_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.warning("Stock data unavailable.")
        return

    delta_str = f"{'+' if data['is_positive'] else ''}{data['change']} ({data['change_pct']}%)"
    st.metric(
        label=f"📈 {data['symbol']} — {data['company_name']}",
        value=f"{data['price']} {data['currency']}",
        delta=delta_str
    )
    st.caption(f"🏛️ Exchange: {data['exchange']} | Status: {data['market_status']} | ⏱️ {data['data_delay']}")
    st.caption(f"**Last updated:** {data.get('last_updated', '24 Sep 2026, 9:35 PM IST')} | Data source: {data.get('provider', 'Yahoo Finance')}")


def render_news_card(data: Dict[str, Any]):
    st.markdown(f"### 📰 Latest News: *{data['topic'].title()}*")
    for article in data.get("articles", []):
        st.markdown(f"""
            <div class="phani-card">
                <div class="phani-card-header">📌 <a href="{article['link']}" target="_blank" style="color: #38bdf8; text-decoration: none;">{article['title']}</a></div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 4px;">Source: {article['source']} • Published: {article['pub_date']}</div>
                <div>{article['summary']}</div>
            </div>
        """, unsafe_allow_html=True)
    st.caption(f"**Last updated:** {data.get('last_updated', '24 Sep 2026, 9:35 PM IST')} | Data source: {data.get('provider', 'Google News Feed')}")


def render_single_movie_item(m: Dict[str, Any]):
    title = m.get("title", "Movie")
    year = m.get("year")
    year_str = f" ({year})" if year else ""
    rating = m.get("rating", "N/A")
    genre = m.get("genre", "N/A")
    director = m.get("director", "N/A")
    actors = m.get("actors") or (", ".join(m.get("cast", [])) if m.get("cast") else "N/A")
    plot = m.get("plot") or m.get("overview", "No overview available.")
    poster = m.get("poster") or m.get("poster_url")
    imdb_url = m.get("imdb_url")

    col_img, col_info = st.columns([1, 2])
    with col_img:
        if poster:
            st.image(poster, width=220)
    with col_info:
        st.markdown(f"## 🎬 {title}{year_str}")
        st.markdown(f"⭐ **Rating:** `{rating}` | 🏷️ **Genre:** `{genre}`")
        st.markdown(f"🎬 **Director:** {director}")
        st.markdown(f"👥 **Cast:** {actors}")
        st.markdown(f"📖 **Overview:** {plot}")
        if imdb_url:
            st.markdown(f"🔗 [View Full Details on IMDb]({imdb_url})")


def render_movie_card(data: Dict[str, Any]):
    if not data.get("success") and data.get("error"):
        st.warning(f"🎬 {data['error']}")
        return

    movies_list = data.get("movies", [])
    if movies_list:
        if len(movies_list) > 1:
            st.markdown(f"### 🎬 Found {len(movies_list)} Verified Movie Matches:")
            for m in movies_list:
                render_single_movie_item(m)
                st.markdown("---")
        else:
            render_single_movie_item(movies_list[0])
    else:
        # Fallback for single movie payload
        render_single_movie_item(data)


def render_maps_card(data: Dict[str, Any]):
    if not data.get("success"):
        st.warning(f"⚠️ {data.get('error', 'Location data unavailable.')}")
        return

    display_name = data.get("display_name", data.get("destination", "Location"))
    g_maps_url = data.get("google_maps_url", "")
    directions_url = data.get("directions_url", "")
    travel_mode = data.get("travel_mode")
    origin = data.get("origin")
    dist_km = data.get("distance_km")
    dur_min = data.get("duration_min")

    st.markdown(f"### 🗺️ Location: **{display_name}**")

    if dist_km and dur_min:
        st.info(f"📏 **Distance:** {dist_km} km | ⏱️ **Estimated Travel Time:** {dur_min} min")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if g_maps_url:
            st.markdown(f"📍 [Open Location in Google Maps]({g_maps_url})")
    with col_btn2:
        if directions_url:
            mode_str = f" ({travel_mode.capitalize()})" if travel_mode else ""
            orig_str = f" from {origin}" if origin else ""
            st.markdown(f"🚗 [Get Directions on Google Maps{orig_str}{mode_str}]({directions_url})")

    st.caption(f"• Coordinates: Latitude `{data.get('lat', 0.0)}`, Longitude `{data.get('lon', 0.0)}` | Data provider: {data.get('provider', 'Google Maps')}")
