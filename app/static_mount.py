from fastapi.staticfiles import StaticFiles
from app.main import app

# Static UI mount
app.mount("/static", StaticFiles(directory="frontend"), name="static")
