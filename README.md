# Civil Radar

Civil Radar is a grassroots protest monitoring app built for public-source discovery and live map tracking.

## What it does

- aggregates public civic activity from public feeds
- detects likely protest activity using simple NLP and keyword scoring
- normalizes location and time clues
- deduplicates repeated reports
- tracks active / stale / dissolved status with TTL logic
- exposes live protest markers on a map via REST and WebSocket
- supports user-submitted reports when the app is running in a browser

## Local startup

```bash
cp .env.example .env
python -m app.db_init
uvicorn app.main:app --reload
```

Then open the app:
- http://localhost:8000/static/index.html
- http://localhost:8000/docs

## Notes

- This app intentionally uses public, legal signal sources rather than private Instagram scraping.
- Demo data is seeded automatically so the map works immediately without external API credentials.
- You can later add real Mastodon, Reddit, or Telegram collectors by filling in credentials in `.env`.
