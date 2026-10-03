from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import SessionLocal
from app.models import Protest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/protests")
def list_protests(db: Session = Depends(get_db)):
    protests = db.query(Protest).filter(Protest.status == "active").all()
    return [serialize_protest(p) for p in protests]


@router.get("/protests/{protest_id}")
def get_protest(protest_id: int, db: Session = Depends(get_db)):
    protest = db.query(Protest).filter(Protest.id == protest_id).first()
    if not protest:
        raise HTTPException(status_code=404, detail="Not found")
    return serialize_protest(protest)


@router.post("/protests")
def create_protest(payload: dict, db: Session = Depends(get_db)):
    dedup_key = payload.get("dedup_key") or f"{payload.get('cause', 'manual')}-{payload.get('location_name', 'unknown')}"
    start_time_raw = payload.get("start_time")
    start_time = datetime.fromisoformat(start_time_raw) if isinstance(start_time_raw, str) else None

    protest = Protest(
        dedup_key=dedup_key,
        cause=payload.get("cause", "general_action"),
        location_name=payload.get("location_name", "Unknown location"),
        latitude=payload.get("latitude"),
        longitude=payload.get("longitude"),
        full_address=payload.get("full_address"),
        start_time=start_time,
        status="active",
        source_count=1,
        sources=[payload.get("source", {"source": "manual"})],
        confidence_score=payload.get("confidence_score", 0.75),
        ttl_hours=payload.get("ttl_hours", 12),
    )
    db.add(protest)
    db.commit()
    db.refresh(protest)
    return serialize_protest(protest)


@router.get("/protests/geojson")
def protests_geojson(db: Session = Depends(get_db)):
    protests = db.query(Protest).filter(Protest.status == "active").all()
    features = []
    for protest in protests:
        if protest.latitude is None or protest.longitude is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(protest.longitude), float(protest.latitude)],
            },
            "properties": {
                "id": protest.id,
                "title": protest.cause or "General action",
                "address": protest.full_address or protest.location_name,
                "status": protest.status,
            },
        })
    return {"type": "FeatureCollection", "features": features}


def serialize_protest(protest: Protest) -> dict:
    return {
        "id": protest.id,
        "dedup_key": protest.dedup_key,
        "cause": protest.cause,
        "location_name": protest.location_name,
        "latitude": protest.latitude,
        "longitude": protest.longitude,
        "full_address": protest.full_address,
        "start_time": protest.start_time.isoformat() if protest.start_time else None,
        "status": protest.status,
        "created_at": protest.created_at.isoformat() if protest.created_at else None,
        "updated_at": protest.updated_at.isoformat() if protest.updated_at else None,
        "last_seen_at": protest.last_seen_at.isoformat() if protest.last_seen_at else None,
        "source_count": protest.source_count,
        "sources": protest.sources,
        "confidence_score": protest.confidence_score,
        "ttl_hours": protest.ttl_hours,
    }
