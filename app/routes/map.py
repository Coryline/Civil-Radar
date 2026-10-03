from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Protest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/map/pins")
def map_pins(db: Session = Depends(get_db)):
    protests = db.query(Protest).filter(Protest.status == "active").all()
    features = []
    for protest in protests:
        if protest.latitude is None or protest.longitude is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(protest.longitude), float(protest.latitude)]
            },
            "properties": {
                "id": protest.id,
                "title": protest.cause or "General action",
                "address": protest.full_address or protest.location_name,
                "status": protest.status,
            }
        })
    return {"type": "FeatureCollection", "features": features}


@router.get("/map/health")
def map_health():
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}
