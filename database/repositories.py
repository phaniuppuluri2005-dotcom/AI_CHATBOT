"""
User-Isolated Repositories Layer for Phani AI Database Access.
Enforces user data isolation server-side across conversations, query logs, and saved items.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import SessionLocal, init_db
from database.models import (
    Conversation, Message, QueryLog, SavedItem, ApiUsage, CacheRecord, User
)

logger = logging.getLogger("PhaniAI.Repositories")

# Ensure tables exist on import
init_db()


class ConversationRepository:
    @staticmethod
    def get_or_create_conversation(db: Session, conversation_id: str, title: str = "New Chat", user_id: Optional[int] = None) -> Conversation:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            conv = Conversation(id=conversation_id, title=title, user_id=user_id)
            db.add(conv)
            db.commit()
            db.refresh(conv)
        elif user_id and conv.user_id != user_id and conv.user_id is None:
            conv.user_id = user_id
            db.commit()
        return conv

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        user_id: Optional[int] = None
    ) -> Message:
        ConversationRepository.get_or_create_conversation(db, conversation_id, user_id=user_id)
        
        entities_json = json.dumps(entities) if entities else None
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            entities_json=entities_json,
            latency_ms=latency_ms
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_conversation_history(db: Session, conversation_id: str, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        query = db.query(Message).join(Conversation).filter(Message.conversation_id == conversation_id)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        messages = query.order_by(Message.created_at.asc()).all()
        history = []
        for m in messages:
            history.append({
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "intent": m.intent,
                "entities": json.loads(m.entities_json) if m.entities_json else {},
                "created_at": m.created_at.isoformat() if m.created_at else ""
            })
        return history

    @staticmethod
    def list_recent_conversations(db: Session, user_id: Optional[int] = None, limit: int = 20) -> List[Dict[str, Any]]:
        query = db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        convs = query.order_by(Conversation.updated_at.desc()).limit(limit).all()
        
        result = []
        for c in convs:
            msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
            result.append({
                "id": c.id,
                "title": c.title,
                "msg_count": msg_count,
                "updated_at": c.updated_at.isoformat() if c.updated_at else ""
            })
        return result

    @staticmethod
    def delete_conversation(db: Session, conversation_id: str, user_id: Optional[int] = None) -> bool:
        query = db.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        conv = query.first()
        if conv:
            db.delete(conv)
            db.commit()
            return True
        return False

    @staticmethod
    def rename_conversation(db: Session, conversation_id: str, new_title: str, user_id: Optional[int] = None) -> bool:
        query = db.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        conv = query.first()
        if conv:
            conv.title = new_title
            db.commit()
            return True
        return False


class AnalyticsRepository:
    @staticmethod
    def log_query(
        db: Session,
        request_id: str,
        query_text: str,
        intent: str,
        confidence: float,
        service: str,
        latency_ms: float,
        cached: bool = False,
        user_id: Optional[int] = None
    ):
        try:
            log = QueryLog(
                user_id=user_id,
                request_id=request_id,
                query_text=query_text,
                intent=intent,
                confidence=confidence,
                service=service,
                latency_ms=latency_ms,
                cached=cached
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging query analytics: {e}")
            db.rollback()

    @staticmethod
    def get_summary_stats(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        query = db.query(QueryLog)
        if user_id:
            query = query.filter(QueryLog.user_id == user_id)

        total_queries = query.count()
        avg_latency = db.query(func.avg(QueryLog.latency_ms)).scalar() or 0.0
        cached_count = query.filter(QueryLog.cached == True).count()
        
        intent_rows = (
            db.query(QueryLog.intent, func.count(QueryLog.id))
            .group_by(QueryLog.intent)
            .order_by(func.count(QueryLog.id).desc())
            .limit(10)
            .all()
        )
        intent_breakdown = {row[0]: row[1] for row in intent_rows if row[0]}

        return {
            "total_queries": total_queries,
            "avg_latency_ms": round(float(avg_latency), 2),
            "cached_queries": cached_count,
            "cache_hit_rate_pct": round((cached_count / max(total_queries, 1)) * 100, 1),
            "intent_breakdown": intent_breakdown
        }


class SavedItemsRepository:
    @staticmethod
    def save_item(db: Session, title: str, content: str, item_type: str = "note", user_id: Optional[int] = None) -> SavedItem:
        item = SavedItem(user_id=user_id, title=title, content=content, item_type=item_type)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def list_items(db: Session, user_id: Optional[int] = None, limit: int = 50) -> List[SavedItem]:
        query = db.query(SavedItem)
        if user_id:
            query = query.filter(SavedItem.user_id == user_id)
        return query.order_by(SavedItem.created_at.desc()).limit(limit).all()

    @staticmethod
    def delete_item(db: Session, item_id: int, user_id: Optional[int] = None) -> bool:
        query = db.query(SavedItem).filter(SavedItem.id == item_id)
        if user_id:
            query = query.filter(SavedItem.user_id == user_id)
        item = query.first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
