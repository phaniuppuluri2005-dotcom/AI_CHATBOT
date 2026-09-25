"""
Interactive Main Unified Chat Interface for Phani AI.
Focuses on 'Ask Phani AI anything' for universal text requests, live real-time information, coding, and explanations.
"""

import time
import streamlit as st
from services.orchestrator import orchestrator
from auth.authentication import get_current_user_dict
from components.cards_ui import (
    render_weather_card, render_cricket_card, render_stock_card,
    render_crypto_card, render_currency_card, render_news_card, render_movie_card, render_maps_card
)
from database.database import SessionLocal
from database.repositories import ConversationRepository, AnalyticsRepository


def render_chat_interface():
    current_user = get_current_user_dict()

    st.title("✨ Ask Phani AI Anything")
    st.caption(f"Logged in as **{current_user['username']}** (`{current_user['email']}`). Ask any question, solve coding tasks, obtain live real-time information, or analyze structured data.")

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = f"phani_session_{int(time.time())}"

    if "previous_context" not in st.session_state:
        st.session_state.previous_context = {}

    # Quick Example Shortcuts
    st.write("💡 **Example Queries:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("💻 Explain Recursion"):
            st.session_state.pending_query = "Explain recursion simply with an example"
    with col2:
        if st.button("🌧️ Weather Hyd"):
            st.session_state.pending_query = "What is the weather in Hyderabad?"
    with col3:
        if st.button("🏏 Live Cricket"):
            st.session_state.pending_query = "What is the current cricket score?"
    with col4:
        if st.button("🪙 Bitcoin Price"):
            st.session_state.pending_query = "Show me current Bitcoin price"
    with col5:
        if st.button("💵 Convert $500"):
            st.session_state.pending_query = "Convert 500 dollars to rupees"

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "cards" in msg:
                for card in msg["cards"]:
                    c_type = card.get("type")
                    data = card.get("data", {})
                    if c_type == "WEATHER":
                        render_weather_card(data)
                    elif c_type == "CRICKET":
                        render_cricket_card(data)
                    elif c_type == "STOCK_MARKET":
                        render_stock_card(data)
                    elif c_type == "CRYPTO":
                        render_crypto_card(data)
                    elif c_type == "CURRENCY":
                        render_currency_card(data)
                    elif c_type == "NEWS":
                        render_news_card(data)
                    elif c_type == "MOVIES":
                        render_movie_card(data)
                    elif c_type == "MAPS":
                        render_maps_card(data)

    # User Input Handling
    user_query = None
    if "pending_query" in st.session_state:
        user_query = st.session_state.pending_query
        del st.session_state.pending_query
    else:
        user_query = st.chat_input("Ask anything — programming, science, math, career, current information, movies, or any other topic...")

    if user_query:
        # Add user message to UI
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Process with Orchestrator
        with st.spinner("Phani AI Reasoning..."):
            res = orchestrator.process_request(
                query=user_query,
                previous_context=st.session_state.previous_context,
                history=st.session_state.messages,
                persona=st.session_state.get("active_persona", "virtual_assistant"),
                user_preference_style=st.session_state.get("user_preference_style", "Balanced")
            )

        # Update previous context
        if "context" in res and res["context"]:
            st.session_state.previous_context.update(res["context"])
        else:
            st.session_state.previous_context = {
                "intent": res["primary_intent"],
                "location": res["entities"].get("location") or st.session_state.previous_context.get("location")
            }

        # Update Sidebar Diagnostics
        st.session_state.diagnostics = {
            "intent": res["primary_intent"],
            "confidence": res["confidence"],
            "confidence_score": res["confidence_score"],
            "entities": res["entities"],
            "latency_ms": res["latency_ms"],
            "service": res["service_summary"]
        }

        # Append Bot Response
        bot_msg = {
            "role": "assistant",
            "content": res["text_response"],
            "cards": res["cards"]
        }
        st.session_state.messages.append(bot_msg)

        # Save to Database with Server-Side User Isolation
        try:
            db = SessionLocal()
            ConversationRepository.add_message(
                db=db,
                conversation_id=st.session_state.session_id,
                role="user",
                content=user_query,
                intent=res["primary_intent"],
                entities=res["entities"],
                user_id=current_user["id"]
            )
            ConversationRepository.add_message(
                db=db,
                conversation_id=st.session_state.session_id,
                role="assistant",
                content=res["text_response"],
                intent=res["primary_intent"],
                latency_ms=res["latency_ms"],
                user_id=current_user["id"]
            )
            AnalyticsRepository.log_query(
                db=db,
                request_id=f"req_{int(time.time())}",
                query_text=user_query,
                intent=res["primary_intent"],
                confidence=res["confidence_score"],
                service=res["service_summary"],
                latency_ms=res["latency_ms"],
                user_id=current_user["id"]
            )
            db.close()
        except Exception as e:
            pass

        st.rerun()
