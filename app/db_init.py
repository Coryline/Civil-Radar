from app.db import engine
from app.models import Base
from app.seed_demo import seed_demo_data


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    print("Civil Radar database initialized.")


if __name__ == "__main__":
    init_db()
