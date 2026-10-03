from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/map/pins")
def map_pins():
    return JSONResponse({
        "type": "FeatureCollection",
        "features": [],
    })
