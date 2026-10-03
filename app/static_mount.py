from fastapi.staticfiles import StaticFiles
from app.main import app

app.mount("/static", StaticFiles(directory="frontend"), name="static")
