from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/map/pins")
def map_pins():
    return JSONResponse({
        "type": "FeatureCollection",
        "features": []
    })


@router.get("/map/health")
def map_health():
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}
