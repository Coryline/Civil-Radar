import json

import praw
import redis

from app.config import settings
from public_sources.common import PublicSourceHarness


class RedditHarvester(PublicSourceHarness):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)
        self.client = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

    def harvest(self):
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return
        subs = ["nyc", "chicago", "losangeles", "seattle", "politics", "activism", "environment", "labour"]
        for sub_name in subs:
            try:
                subreddit = self.client.subreddit(sub_name)
                for submission in subreddit.new(limit=12):
                    text = self.clean_text(f"{submission.title}\n{submission.selftext}")
                    if not text:
                        continue
                    payload = {
                        "source": "reddit",
                        "source_id": str(submission.id),
                        "text": text,
                        "url": f"https://reddit.com{submission.permalink}",
                        "author": getattr(submission.author, "name", "deleted"),
                    }
                    self.redis.lpush("civilradar:raw", json.dumps(payload))
            except Exception:
                continue
