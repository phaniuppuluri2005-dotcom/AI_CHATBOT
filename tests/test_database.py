"""
Automated Test Suite for Phani AI Database and Repositories.
"""

from database.database import SessionLocal, init_db
from database.repositories import ConversationRepository, AnalyticsRepository


def test_conversation_logging():
    init_db()
    db_session = SessionLocal()
    try:
        conv_id = "test_session_123"
        msg_user = ConversationRepository.add_message(
            db=db_session,
            conversation_id=conv_id,
            role="user",
            content="What is the weather in Hyderabad?",
            intent="WEATHER"
        )
        assert msg_user.id is not None
        assert msg_user.intent == "WEATHER"

        history = ConversationRepository.get_conversation_history(db_session, conv_id)
        assert len(history) >= 1
        assert history[0]["content"] == "What is the weather in Hyderabad?"
    finally:
        db_session.close()


def test_analytics_summary():
    init_db()
    db_session = SessionLocal()
    try:
        AnalyticsRepository.log_query(
            db=db_session,
            request_id="req_test_1",
            query_text="Convert 50 USD to INR",
            intent="CURRENCY",
            confidence=0.95,
            service="Currency API",
            latency_ms=12.5,
            cached=False
        )
        stats = AnalyticsRepository.get_summary_stats(db_session)
        assert stats["total_queries"] > 0
        assert "CURRENCY" in stats["intent_breakdown"]
    finally:
        db_session.close()
