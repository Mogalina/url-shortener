import logging
from datetime import timedelta
from app.db.cassandra import session
from app.db.redis import redis
from app.utils.id_generator import generate_short_code
from app.utils.time import now

logger = logging.getLogger("service.shortener")

def create_short_url(long_url: str, ttl_days: int):
    logger.info("Creating short URL")

    code = generate_short_code()
    expires = now() + timedelta(days=ttl_days)

    session.execute(
        """
        INSERT INTO urls (short_code, long_url, created_at, expires_at)
        VALUES (%s, %s, %s, %s)
        """,
        (code, long_url, now(), expires)
    )

    logger.info("Saved URL in Cassandra", extra={"code": code})

    redis.set(f"short:{code}", ttl_days * 86400, long_url)
    logger.info("Cached URL in Redis", extra={"code": code})

    return code
