import logging
from datetime import datetime
from app.db.cassandra import session
from app.db.redis import redis
from app.core.config import settings

logger = logging.getLogger("service.resolver")

def resolve_url(code: str):
    logger.info("Resolving short code", extra={"code": code})

    cached = redis.get(f"short:{code}")
    if cached:
        logger.info("Cache hit", extra={"code": code})
        return cached

    logger.info("Cache miss", extra={"code": code})

    row = session.execute(
        """SELECT long_url, expires_at 
        FROM urls 
        WHERE short_code = %s
        """,
        (code,)
    ).one()

    if not row:
        logger.warning("Code not found in Cassandra", extra={"code": code})
        return None

    if row.expires_at < datetime.now():
        logger.warning("Code expired", extra={"code": code})
        return None

    redis.set(f"short:{code}", row.long_url, ex=settings.CACHE_TTL_SECONDS)
    logger.info("Cache repopulated", extra={"code": code})

    return row.long_url
