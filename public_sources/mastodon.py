from mastodon import Mastodon
from app.config import settings
from public_sources.common import PublicSourceHarness
import json
import redis


class MastodonHarvester(PublicSourceHarness):
    def __init__(self):
        self.client = Mastodon(api_base_url=settings.mastodon_api_base, access_token=settings.mastodon_bearer)
        self.redis = redis.Redis.from_url(settings.redis_url)

    def harvest(self):
        for tag in ["protest", "rally", "march", "demonstration", "activism"]:
            try:
                public_timeline = self.client.timeline_hashtag(tag, limit=20)
                for item in public_timeline:
                    payload = {
                        "source": "mastodon",
                        "source_id": str(item.get("id")),
                        "text": self.clean_text(item.get("content")),
                        "url": item.get("url"),
                        "author": item.get("account", {}).get("username"),
                    }
                    if payload["text"]:
                        self.redis.lpush("civilradar:raw", json.dumps(payload))
            except Exception:
                continue
