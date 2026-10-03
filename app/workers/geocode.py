import hashlib
from datetime import datetime, timedelta
from typing import Optional

from geopy.geocoders import Nominatim
from dateparser import parse as parse_date


class EventGeocoder:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="Civil-Radar")

    def normalize(self, classification: dict) -> dict:
        locations = classification.get("locations", [])
        geocoded = []

        for location in locations:
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
                pass

        event_time = self._infer_time(classification.get("times"))
        cause = self._infer_cause(classification.get("text", ""))

        if not geocoded:
            geocoded.append({
                "name": "Unknown location",
                "lat": None,
                "lng": None,
                "address": None,
            })

        dedup_key = hashlib.md5(
            f"{geocoded[0]['name']}|{cause}|{event_time.date().isoformat()}".encode()
        ).hexdigest()

        return {
            "dedup_key": dedup_key,
            "cause": cause,
            "location_name": geocoded[0]["name"],
            "latitude": geocoded[0]["lat"],
            "longitude": geocoded[0]["lng"],
            "full_address": geocoded[0]["address"],
            "start_time": event_time,
            "status": "active",
            "confidence_score": classification.get("score", 0.7),
            "source": classification.get("source"),
            "source_id": classification.get("source_id"),
            "url": classification.get("url"),
            "author": classification.get("author"),
            "raw_text": classification.get("text", ""),
            "ttl_hours": 12,
        }

    def _infer_time(self, times: Optional[list[str]]) -> datetime:
        if times:
            parsed = parse_date(times[0])
            if parsed:
                return parsed
        return datetime.utcnow() + timedelta(hours=6)

    def _infer_cause(self, text: str) -> str:
        lowered = text.lower()
        mappings = {
            "labor": ["labor", "union", "worker", "wages", "strike"],
            "climate": ["climate", "environment", "carbon", "green"],
            "racial_justice": ["blm", "racism", "police", "justice"],
            "housing": ["housing", "rent", "eviction", "tenant"],
            "democracy": ["vote", "election", "voting", "democracy"],
        }
        for cause, keywords in mappings.items():
            if any(keyword in lowered for keyword in keywords):
                return cause
        return "general_action"
