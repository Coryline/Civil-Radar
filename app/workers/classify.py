import json
import re
from typing import Optional


ACTION_KEYWORDS = {
    "protest": ["protest", "march", "rally", "demonstration", "strike", "gather", "action", "blockade", "sit-in", "standwith"],
    "labor": ["labor", "workers", "union", "wages", "strike"],
    "climate": ["climate", "environment", "green", "carbon", "fossil"],
    "racial_justice": ["blm", "racism", "police", "justice", "solidarity"],
    "housing": ["housing", "rent", "eviction", "tenant"],
    "democracy": ["vote", "democracy", "election", "voting"],
}


class ProtestClassifier:
    def classify(self, raw_event: dict) -> Optional[dict]:
        text = raw_event.get("text", "")
        if not text:
            return None

        lowered = text.lower()
        score = 0.0
        reasons = []

        for cause, keywords in ACTION_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                score += 0.2
                reasons.append(cause)

        if any(word in lowered for word in ["protest", "march", "rally", "demonstration", "strike"]):
            score += 0.5

        if score < 0.5:
            return None

        location_candidates = self._extract_locations(text)
        time_candidates = self._extract_times(text)

        return {
            "source": raw_event.get("source"),
            "source_id": raw_event.get("source_id"),
            "text": text,
            "url": raw_event.get("url"),
            "author": raw_event.get("author"),
            "score": round(score, 2),
            "locations": location_candidates,
            "times": time_candidates,
            "reasons": reasons,
        }

    def _extract_locations(self, text: str) -> list[str]:
        patterns = [
            r"(?:at|outside|near|in|from)\s+([A-Z][A-Za-z0-9'\-., ]+)",
            r"([A-Z][A-Za-z0-9'\-., ]+\s+(?:Street|Ave|Avenue|Road|Blvd|Boulevard|Park|Square|Plaza|Center|Hall|Station))",
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return [m.strip() for m in matches if m.strip()]

    def _extract_times(self, text: str) -> list[str]:
        time_phrases = re.findall(r"\b(?:today|tomorrow|tonight|this Friday|this Saturday|this Sunday|next Monday|next Tuesday|next Wednesday|next Thursday|next Friday|next Saturday|next Sunday)\b", text, flags=re.I)
        if time_phrases:
            return time_phrases
        return []
