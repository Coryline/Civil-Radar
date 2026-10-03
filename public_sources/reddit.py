import json
import praw
import redis
from app.config import settings
from public_sources.common import PublicSourceHarness


class RedditHarvester(PublicSourceHarness):
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        self.redis = redis.Redis.from_url(settings.redis_url)

    def harvest(self):
        active_subs = ["nyc", "chicago", "losangeles", "politics", "activism", "labour", "environment"]
        for sub_name in active_subs:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                for submission in subreddit.new(limit=25):
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
