from __future__ import annotations

import json
import threading
import time

import redis

from app.config import settings
from app.workers.tasks import EventProcessor
from public_sources.mastodon import MastodonHarvester
from public_sources.reddit import RedditHarvester
from public_sources.telegram import TelegramHarvester


class PublicFeedCollector:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        self.processor = EventProcessor()
        self.harvesters = [
            MastodonHarvester(),
            RedditHarvester(),
            TelegramHarvester(),
        ]

    def run_once(self):
        for harvester in self.harvesters:
            try:
                if hasattr(harvester, "harvest"):
                    harvester.harvest()
            except Exception:
                continue

        while True:
            item = self.redis.blpop("civilradar:raw", timeout=1)
            if item is None:
                break
            _, payload = item
            event = json.loads(payload)
            self.processor.process(event)

    def run_forever(self, interval_seconds: int = 30):
        while True:
            self.run_once()
            time.sleep(interval_seconds)


def start_ingestion_worker():
    collector = PublicFeedCollector()
    thread = threading.Thread(target=collector.run_forever, daemon=True)
    thread.start()
    return thread
