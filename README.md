# Civil Radar

Civil Radar is a real-time protest monitoring platform for grassroots civic action. It ingests public social and community sources, classifies likely protest activity, geocodes events, deduplicates repeated reports, tracks live TTL status, and exposes the data through a map-driven frontend.

## Architecture

- Public source harvesters: Mastodon, Reddit, Telegram
- Event classification: NLP + rule-based filters
- Geocoding: OpenStreetMap / Mapbox
- Storage: PostgreSQL with PostGIS
- Queue: Redis + Celery
- Real-time updates: FastAPI WebSockets
- Frontend: Mapbox GL JS / Leaflet-style UI

## Local development

```bash
cp .env.example .env

docker compose up --build
```

Then open:
- API: http://localhost:8000/docs
- Map frontend: http://localhost:8000/static/index.html

## Notes

- This project intentionally avoids private Instagram scraping.
- It focuses on public, legal, community-driven signal sources.
- The ingestion pipeline is designed for real-time grassroots discovery rather than luxury campaign-style event listings.

## Commands

```bash
# Start the stack

docker compose up

# Run migrations / schema creation manually if needed
python -m app.db_init
```

## License

MIT
