from app.workers.classify import ProtestClassifier
from app.workers.geocode import EventGeocoder
from app.workers.dedupe import EventDeduplicator
import json
import redis

class IngestionWorker:
    def __init__(self):
        self.redis = redis.Redis.from_url("redis://redis:6379/0")
        self.classifier = ProtestClassifier()
        self.geocoder = EventGeocoder()
        self.dedupe = EventDeduplicator()

    def process_raw_event(self, raw_event: dict):
        classification = self.classifier.classify(raw_event)
        if not classification:
            return

        normalized = self.geocoder.normalize(classification)
        self.dedupe.insert_or_update(normalized)

    def run_forever(self):
        while True:
            item = self.redis.blpop("civilradar:raw", timeout=5)
            if not item:
                continue
            _, payload = item
            self.process_raw_event(json.loads(payload))
