# Civil Radar

This is the beginning of the Civil Radar project.

It currently includes:
- FastAPI scaffold
- PostgreSQL + PostGIS-ready model
- Redis-backed worker structure
- public-source harvesters for Mastodon, Reddit, and Telegram
- map frontend shell

## Next steps

1. Add the database setup migration.
2. Add the NLP event classification pipeline and polling.
3. Add a TTL sweep task and websocket push updates.
4. Add a detailed protest detail page and cluster layout.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then visit:
- http://localhost:8000/docs
- http://localhost:8000/static/index.html
