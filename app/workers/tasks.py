import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Optional

import dateparser
import redis
from geopy.geocoders import Nominatim

from app.config import settings


class ProtestClassifier:
    def classify(self, payload: dict) -> Optional[dict]:
        text = payload.get("text", "")
        if not text:
            return None

        lowered = text.lower()
        weights = {
            "protest": ["protest", "rally", "march", "demonstration", "strike", "gathering", "walkout"],
            "labor": ["labor", "union", "wages", "worker"],
            "climate": ["climate", "environment", "green", "carbon"],
            "racial_justice": ["police", "racism", "justice", "blm"],
            "housing": ["housing", "rent", "eviction"],
            "democracy": ["vote", "voting", "democracy", "election"],
        }

        score = 0.0
        reasons = []
        for cause, words in weights.items():
            if any(word in lowered for word in words):
                score += 0.25
                reasons.append(cause)

        if any(word in lowered for word in ["protest", "march", "rally", "demo", "strike"]):
            score += 0.5

        if score < 0.5:
            return None

        return {
            "source": payload.get("source"),
            "source_id": payload.get("source_id"),
            "text": text,
            "url": payload.get("url"),
            "author": payload.get("author"),
            "score": score,
            "locations": self._extract_locations(text),
            "times": self._extract_times(text),
            "reasons": reasons,
        }

    def _extract_locations(self, text: str) -> list[str]:
        patterns = [
            r"(?:at|near|outside|in|outside of)\s+([A-Z][A-Za-z0-9'\-., ]+)",
            r"([A-Z][A-Za-z0-9'\-., ]+\s(?:Street|Ave|Avenue|Road|Blvd|Boulevard|Square|Park|Hall|Center|Plaza))",
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return [m.strip() for m in matches if m.strip()]

    def _extract_times(self, text: str) -> list[str]:
        patterns = [
            r"\b(?:today|tomorrow|tonight|this Friday|this Saturday|this Sunday|next Monday|next Tuesday|next Wednesday|next Thursday|next Friday|next Saturday|next Sunday)\b",
            r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
        ]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text, flags=re.I))
        return found


class EventGeocoder:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="Civil-Radar")

    def normalize(self, classification: dict) -> dict:
        location_candidates = classification.get("locations", [])
        geocoded = []
        for location in location_candidates:
            try:
                result = self.geocoder.geocode(location, timeout=10)
                if result:
                    geocoded.append({
                        "name": location,
                        "lat": result.latitude,
                        "lng": result.longitude,
                        "address": result.address,
                    })
            except Exception:
                continue

        if not geocoded:
            geocoded.append({"name": "Unknown location", "lat": None, "lng": None, "address": None})

        cause = self._infer_cause(classification.get("text", ""))
        start_time = self._infer_start_time(classification.get("times"))
        dedup_key = hashlib.md5(
            f"{geocoded[0]['name']}|{cause}|{start_time.date().isoformat()}".encode()
        ).hexdigest()

        return {
            "dedup_key": dedup_key,
            "cause": cause,
            "location_name": geocoded[0]["name"],
            "latitude": geocoded[0]["lat"],
            "longitude": geocoded[0]["lng"],
            "full_address": geocoded[0]["address"],
            "start_time": start_time,
            "status": "active",
            "source": classification.get("source"),
            "source_id": classification.get("source_id"),
            "url": classification.get("url"),
            "author": classification.get("author"),
            "confidence_score": classification.get("score", 0.75),
            "ttl_hours": 12,
            "raw_text": classification.get("text"),
        }

    def _infer_cause(self, text: str) -> str:
        lowered = text.lower()
        mapping = {
            "labor": ["labor", "union", "worker", "wages", "strike"],
            "climate": ["climate", "environment", "green", "carbon"],
            "racial_justice": ["blm", "police", "racism", "justice"],
            "housing": ["housing", "rent", "eviction", "tenant"],
            "democracy": ["vote", "election", "voting", "democracy"],
        }
        for cause, terms in mapping.items():
            if any(term in lowered for term in terms):
                return cause
        return "general_action"

    def _infer_start_time(self, time_candidates: list[str]) -> datetime:
        if time_candidates:
            parsed = dateparser.parse(time_candidates[0])
            if parsed:
                return parsed
        return datetime.utcnow() + timedelta(hours=6)


class EventProcessor:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        self.classifier = ProtestClassifier()
        self.geocoder = EventGeocoder()

    def process(self, payload: dict):
        classification = self.classifier.classify(payload)
        if not classification:
            return None

        normalized = self.geocoder.normalize(classification)
        self.redis.lpush("civilradar:normalized", json.dumps(normalized))
        return normalized
