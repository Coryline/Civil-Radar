from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.protests import router as protests_router
from app.routes.map import router as map_router
from app.websocket_manager import manager

app = FastAPI(title="Civil Radar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(protests_router, prefix="/api")
app.include_router(map_router, prefix="/api")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.websocket("/ws/map")
async def map_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        await manager.disconnect(websocket)
