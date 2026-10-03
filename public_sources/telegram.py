import json
import redis
from telethon import TelegramClient
from app.config import settings
from public_sources.common import PublicSourceHarness


class TelegramHarvester(PublicSourceHarness):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        self.client = TelegramClient("civilradar_session", settings.telegram_api_id, settings.telegram_api_hash)
        self.channels = ["demonstrations", "localaction", "communityactions", "activismnews"]

    async def harvest(self):
        await self.client.start()
        for channel in self.channels:
            try:
                entity = await self.client.get_entity(channel)
                async for message in self.client.iter_messages(entity, limit=25):
                    text = self.clean_text(message.text)
                    if not text:
                        continue
                    payload = {
                        "source": "telegram",
                        "source_id": str(message.id),
                        "text": text,
                        "url": f"https://t.me/{channel}/{message.id}",
                        "author": getattr(message.sender, "username", "unknown"),
                    }
                    self.redis.lpush("civilradar:raw", json.dumps(payload))
            except Exception:
                continue
