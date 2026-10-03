from datetime import datetime

from app.db import SessionLocal
from app.models import Protest


DEMO_PROTESTS = [
    {
        "dedup_key": "demo-nyc-labor-2026-10-03",
        "cause": "Labor rights",
        "location_name": "Union Square",
        "latitude": 40.7359,
        "longitude": -73.9911,
        "full_address": "Union Square, New York, NY",
        "start_time": "2026-10-03T17:00:00",
        "status": "active",
        "source_count": 3,
        "sources": [
            {"source": "mastodon", "source_id": "m-001", "url": "https://example.com/m-001", "author": "localvoice"},
            {"source": "reddit", "source_id": "r-001", "url": "https://example.com/r-001", "author": "nycactivist"},
            {"source": "user_report", "source_id": "u-001", "url": "https://example.com/u-001", "author": "anonymous"},
        ],
        "confidence_score": 0.92,
        "ttl_hours": 12,
    },
    {
        "dedup_key": "demo-la-climate-2026-10-03",
        "cause": "Climate action",
        "location_name": "MacArthur Park",
        "latitude": 34.0585,
        "longitude": -118.2783,
        "full_address": "MacArthur Park, Los Angeles, CA",
        "start_time": "2026-10-03T18:30:00",
        "status": "active",
        "source_count": 2,
        "sources": [
            {"source": "telegram", "source_id": "t-001", "url": "https://example.com/t-001", "author": "laaction"},
            {"source": "reddit", "source_id": "r-002", "url": "https://example.com/r-002", "author": "ca_organizer"},
        ],
        "confidence_score": 0.88,
        "ttl_hours": 12,
    },
    {
        "dedup_key": "demo-seattle-democracy-2026-10-03",
        "cause": "Democracy rights",
        "location_name": "Seattle Center",
        "latitude": 47.6211,
        "longitude": -122.3493,
        "full_address": "Seattle Center, Seattle, WA",
        "start_time": "2026-10-03T16:15:00",
        "status": "active",
        "source_count": 2,
        "sources": [
            {"source": "mastodon", "source_id": "m-010", "url": "https://example.com/m-010", "author": "civicwatch"},
            {"source": "user_report", "source_id": "u-010", "url": "https://example.com/u-010", "author": "observer"},
        ],
        "confidence_score": 0.85,
        "ttl_hours": 12,
    },
]


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        count = db.query(Protest).count()
        if count > 0:
            return

        for item in DEMO_PROTESTS:
            protest = Protest(
                dedup_key=item["dedup_key"],
                cause=item["cause"],
                location_name=item["location_name"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                full_address=item["full_address"],
                start_time=datetime.fromisoformat(item["start_time"]),
                status=item["status"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                source_count=item["source_count"],
                sources=item["sources"],
                confidence_score=item["confidence_score"],
                ttl_hours=item["ttl_hours"],
            )
            db.add(protest)
        db.commit()
    finally:
        db.close()
