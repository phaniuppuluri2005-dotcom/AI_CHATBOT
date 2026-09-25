"""
Live Real-Time Services Hub Component for Phani AI.
Interactive tabbed dashboard for manual lookup across Weather, Sports, News, Finance, Crypto, Forex, Maps, Movies, Translation, and Wikipedia.
Enforces exact live timestamp formatting across all live service tabs.
"""

import streamlit as st
from services.weather_service import weather_service
from services.cricket_service import cricket_service
from services.news_service import news_service
from services.stock_service import stock_service
from services.crypto_service import crypto_service
from services.currency_service import currency_service
from services.maps_service import maps_service
from services.movies_service import movies_service
from services.translation_service import translation_service
from services.wikipedia_service import wikipedia_service

from components.cards_ui import (
    render_weather_card, render_cricket_card, render_stock_card,
    render_crypto_card, render_currency_card, render_news_card, render_movie_card, render_maps_card
)


def render_live_services_page():
    st.title("🌐 Phani AI — Real-Time Services Hub")
    st.caption("Access live weather forecasts, sports scores, stock prices, crypto stats, universal forex conversion, breaking news, movie lookup, and translations.")

    tab_weather, tab_cricket, tab_news, tab_stocks, tab_crypto, tab_forex, tab_maps, tab_movies, tab_trans, tab_wiki = st.tabs([
        "🌤️ Weather", "🏏 Cricket", "📰 News", "📈 Stocks", "🪙 Crypto", "💱 Currency", "🗺️ Maps", "🎬 Movies", "🌐 Translation", "📚 Knowledge"
    ])

    with tab_weather:
        col1, col2 = st.columns([3, 1])
        with col1:
            city = st.text_input("Enter City Name", value="Hyderabad", key="live_weather_city")
        with col2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_w = st.button("Check Weather")
        if btn_w or city:
            data = weather_service.get_weather(city)
            render_weather_card(data)

    with tab_cricket:
        data_c = cricket_service.get_live_scores()
        render_cricket_card(data_c)

    with tab_news:
        topic = st.text_input("Search News Topic", value="technology", key="live_news_topic")
        if topic:
            data_n = news_service.get_news(topic)
            render_news_card(data_n)

    with tab_stocks:
        symbol = st.text_input("Enter Stock Ticker Symbol", value="AAPL", key="live_stock_sym").upper()
        if symbol:
            data_s = stock_service.get_stock_price(symbol)
            render_stock_card(data_s)

    with tab_crypto:
        asset = st.selectbox("Select Crypto Asset", ["Bitcoin", "Ethereum", "Solana", "Dogecoin"])
        data_cr = crypto_service.get_crypto_price(asset)
        render_crypto_card(data_cr)

    with tab_forex:
        st.markdown("### 💱 Universal Currency Converter")

        supported_list = currency_service.get_supported_currencies()
        code_options = [item["code"] for item in supported_list]
        display_map = {item["code"]: item["display"] for item in supported_list}

        # Initialize session state for currency selectboxes
        if "forex_from" not in st.session_state:
            st.session_state.forex_from = "USD"
        if "forex_to" not in st.session_state:
            st.session_state.forex_to = "INR"

        col_amt, col_from, col_swap, col_to = st.columns([2, 3, 1, 3])
        with col_amt:
            amt = st.number_input("Amount", value=100.0, step=10.0, key="forex_amount_input")
        with col_from:
            idx_from = code_options.index(st.session_state.forex_from) if st.session_state.forex_from in code_options else 0
            selected_from = st.selectbox(
                "From Currency",
                code_options,
                index=idx_from,
                format_func=lambda c: display_map.get(c, c),
                key="forex_from_select"
            )
            st.session_state.forex_from = selected_from

        with col_swap:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Swap", key="swap_currencies_btn"):
                # Swap session state values
                old_from = st.session_state.forex_from
                st.session_state.forex_from = st.session_state.forex_to
                st.session_state.forex_to = old_from
                st.rerun()

        with col_to:
            idx_to = code_options.index(st.session_state.forex_to) if st.session_state.forex_to in code_options else 1
            selected_to = st.selectbox(
                "To Currency",
                code_options,
                index=idx_to,
                format_func=lambda c: display_map.get(c, c),
                key="forex_to_select"
            )
            st.session_state.forex_to = selected_to

        if st.button("Convert Currency", type="primary"):
            conv = currency_service.convert(amt, st.session_state.forex_from, st.session_state.forex_to)
            render_currency_card(conv)
        else:
            # Render default conversion result on load
            conv = currency_service.convert(amt, st.session_state.forex_from, st.session_state.forex_to)
            render_currency_card(conv)

    with tab_maps:
        loc_q = st.text_input("Search Map Location", value="Hyderabad, India")
        if loc_q:
            loc = maps_service.search_location(loc_q)
            render_maps_card(loc)

    with tab_movies:
        movie_title = st.text_input("Search Movie Title", value="Inception")
        if movie_title:
            m_data = movies_service.search_movie(movie_title)
            render_movie_card(m_data)

    with tab_trans:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_text = st.text_area("Source Text", value="What is the weather in Hyderabad today?", height=100)
        with col_t2:
            t_target = st.selectbox("Target Language", ["Telugu", "Hindi", "Spanish", "French", "German"])

        if st.button("Translate Text"):
            tr_res = translation_service.translate(t_text, target_lang=t_target)
            st.markdown(f"### 🌐 Translation Result ({t_target}):")
            st.info(tr_res["translated_text"])

    with tab_wiki:
        w_query = st.text_input("Wikipedia Knowledge Lookup", value="Artificial Intelligence")
        if w_query:
            w_res = wikipedia_service.get_summary(w_query)
            if w_res.get("success"):
                st.markdown(f"## 📚 {w_res['title']}")
                st.write(w_res["summary"])
                st.markdown(f"🔗 [Read Full Wikipedia Article]({w_res['url']})")
