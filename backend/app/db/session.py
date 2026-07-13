from sqlalchemy import text

from app.db.database import engine
from app.db.database import SessionLocal

from app.logging import setup_logger

logger = setup_logger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_pgvector_extension():
    """Enable pgvector extension before any table with VECTOR columns is created"""
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled")
        except Exception as e:
            logger.error(f"Failed to enable pgvector extension: {e}. Is pgvector installed on this Postgres instance?")
            raise