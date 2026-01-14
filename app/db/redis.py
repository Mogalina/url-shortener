import logging
from redis import Redis
from redis.cluster import RedisCluster, ClusterNode
from app.core.config import settings

logger = logging.getLogger("redis")

if "," in settings.REDIS_HOST:
    logger.info("Initializing Redis Cluster connection...")

    startup_nodes = [
        ClusterNode(host.strip(), settings.REDIS_PORT) 
        for host in settings.REDIS_HOST.split(",")
    ]
    
    redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
else:
    logger.info("Initializing Single Redis Node connection...")
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )

logger.info("Redis client initialized")
