from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@db:5432/protests"
    redis_url: str = "redis://redis:6379/0"
    mapbox_token: str = ""
    mastodon_api_base: str = "https://mastodon.social"
    mastodon_bearer: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "Civil-Radar"
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    app_env: str = "development"

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False


settings = Settings()
