from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Protest(Base):
    __tablename__ = "protests"

    id = Column(Integer, primary_key=True, index=True)
    dedup_key = Column(String, unique=True, index=True)
    cause = Column(String, nullable=True)
    location_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    full_address = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    source_count = Column(Integer, default=1)
    sources = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.0)
    ttl_hours = Column(Integer, default=12)
