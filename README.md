# Civil Radar

Civil Radar is a grassroots protest monitoring app built for public-source discovery and live map tracking.

## What it does

- Aggregates public civic activity from public feeds
- Detects likely protest activity from text signals
- Normalizes location and time data
- Deduplicates repeated reports
- Tracks active / stale / dissolved status with TTL logic
- Displays live protest markers on a map
- Enables user-reported updates and event detail pages

## Local startup

```bash
cp .env.example .env

docker compose up --build
```

Then open the app:
- http://localhost:8000/static/index.html
- http://localhost:8000/docs

## Notes

- This app intentionally uses public, legal signal sources rather than private Instagram scraping.
- Demo data is seeded automatically so the map works immediately without external API credentials.
- You can later add real Mastodon, Reddit, or Telegram collectors by filling in credentials in `.env`.
