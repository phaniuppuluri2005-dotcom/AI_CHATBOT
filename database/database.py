"""
Database Connection & Session Factory for Phani AI.
Configured via settings.DATABASE_URL (SQLite or PostgreSQL).
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import settings
from database.models import Base

logger = logging.getLogger("PhaniAI.Database")

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)


def init_db():
    """Create all tables in the database if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")


def get_db():
    """Dependency / helper for database session retrieval."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
