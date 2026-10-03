from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

fallback_db_url = "sqlite:///./civil_radar.db"

try:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception:
    engine = create_engine(fallback_db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
