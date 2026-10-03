import json

import redis
from telethon import TelegramClient

from app.config import settings
from public_sources.common import PublicSourceHarness


class TelegramHarvester(PublicSourceHarness):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        if not settings.telegram_api_id or not settings.telegram_api_hash:
            self.client = None
        else:
            self.client = TelegramClient("civilradar_session", settings.telegram_api_id, settings.telegram_api_hash)

    async def harvest(self):
        if self.client is None:
            return
        try:
            await self.client.start()
            for channel in ["localaction", "communityactions", "activismnews", "demonstrations"]:
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
        except Exception:
            return
