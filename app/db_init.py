from app.db import engine
from app.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Civil Radar database initialized.")


if __name__ == "__main__":
    init_db()
