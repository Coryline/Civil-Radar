from datetime import datetime
import json
import sqlalchemy
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Protest


class EventDeduplicator:
    def insert_or_update(self, payload: dict):
        db: Session = SessionLocal()
        try:
            existing = db.query(Protest).filter(Protest.dedup_key == payload["dedup_key"]).first()
            if existing:
                existing.updated_at = datetime.utcnow()
                existing.last_seen_at = datetime.utcnow()
                existing.status = "active"
                existing.source_count = (existing.source_count or 0) + 1
                existing.sources = (existing.sources or []) + [{
                    "source": payload.get("source"),
                    "source_id": payload.get("source_id"),
                    "url": payload.get("url"),
                    "author": payload.get("author"),
                }]
                existing.confidence_score = max(existing.confidence_score or 0.0, payload.get("confidence_score", 0.0))
            else:
                protest = Protest(
                    dedup_key=payload["dedup_key"],
                    cause=payload.get("cause"),
                    location_name=payload.get("location_name"),
                    latitude=payload.get("latitude"),
                    longitude=payload.get("longitude"),
                    full_address=payload.get("full_address"),
                    start_time=payload.get("start_time"),
                    status="active",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    source_count=1,
                    sources=[{
                        "source": payload.get("source"),
                        "source_id": payload.get("source_id"),
                        "url": payload.get("url"),
                        "author": payload.get("author"),
                    }],
                    confidence_score=payload.get("confidence_score", 0.0),
                    ttl_hours=payload.get("ttl_hours", 12),
                )
                db.add(protest)
            db.commit()
        finally:
            db.close()
