import json
from datetime import datetime

import redis
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import Protest


class EventWriter:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)

    def consume(self):
        while True:
            item = self.redis.blpop("civilradar:normalized", timeout=5)
            if item is None:
                continue
            _, payload = item
            event = json.loads(payload)
            self.write(event)

    def write(self, event: dict):
        db: Session = SessionLocal()
        try:
            existing = db.query(Protest).filter(Protest.dedup_key == event["dedup_key"]).first()
            if existing:
                existing.updated_at = datetime.utcnow()
                existing.last_seen_at = datetime.utcnow()
                existing.status = "active"
                existing.source_count = (existing.source_count or 0) + 1
                existing.confidence_score = max(existing.confidence_score, event.get("confidence_score", 0))
                existing.sources = (existing.sources or []) + [{
                    "source": event.get("source"),
                    "source_id": event.get("source_id"),
                    "url": event.get("url"),
                    "author": event.get("author"),
                }]
            else:
                db.add(Protest(
                    dedup_key=event["dedup_key"],
                    cause=event.get("cause"),
                    location_name=event.get("location_name"),
                    latitude=event.get("latitude"),
                    longitude=event.get("longitude"),
                    full_address=event.get("full_address"),
                    start_time=event.get("start_time"),
                    status="active",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    source_count=1,
                    sources=[{
                        "source": event.get("source"),
                        "source_id": event.get("source_id"),
                        "url": event.get("url"),
                        "author": event.get("author"),
                    }],
                    confidence_score=event.get("confidence_score", 0.0),
                    ttl_hours=event.get("ttl_hours", 12),
                ))
            db.commit()
        finally:
            db.close()
