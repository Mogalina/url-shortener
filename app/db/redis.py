import redis
import logging
from app.core.config import settings

logger = logging.getLogger("redis")

redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

logger.info("Redis client initialized")
