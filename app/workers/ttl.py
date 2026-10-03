from datetime import datetime
from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


class TTLWorker:
    def sweep(self):
        with engine.begin() as connection:
            stale = connection.execute(text("""
                UPDATE protests
                SET status = 'stale', updated_at = NOW()
                WHERE status = 'active' AND last_seen_at < NOW() - INTERVAL '3 hours'
            """))

            dissolved = connection.execute(text("""
                UPDATE protests
                SET status = 'dissolved', updated_at = NOW()
                WHERE status = 'stale' AND last_seen_at < NOW() - INTERVAL '12 hours'
            """))

            connection.commit()
            return {"stale_rows": stale.rowcount, "dissolved_rows": dissolved.rowcount}
