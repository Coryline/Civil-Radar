from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.map import router as map_router
from app.routes.protests import router as protests_router

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
