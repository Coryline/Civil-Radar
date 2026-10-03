import json

import redis
from mastodon import Mastodon

from app.config import settings
from public_sources.common import PublicSourceHarness


class MastodonHarvester(PublicSourceHarness):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        self.client = Mastodon(api_base_url=settings.mastodon_api_base, access_token=settings.mastodon_bearer)

    def harvest(self):
        if not settings.mastodon_bearer:
            return
        for tag in ["protest", "rally", "march", "demonstration", "activism", "solidarity"]:
            try:
                for item in self.client.timeline_hashtag(tag, limit=15):
                    text = self.clean_text(item.get("content"))
                    if not text:
                        continue
                    payload = {
                        "source": "mastodon",
                        "source_id": str(item.get("id")),
                        "text": text,
                        "url": item.get("url"),
                        "author": item.get("account", {}).get("username"),
                    }
                    self.redis.lpush("civilradar:raw", json.dumps(payload))
            except Exception:
                continue
