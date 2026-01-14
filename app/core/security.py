import logging
from fastapi import Request, HTTPException
from app.db.redis import redis

logger = logging.getLogger("security.rate_limit")

RATE_LIMIT = 10
WINDOW_SECONDS = 60

def rate_limit(request: Request):
    client_ip = request.client.host
    key = f"rl:{client_ip}"

    try:
        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, WINDOW_SECONDS, nx=True) 
        result = pipe.execute()
        
        current = result[0]

        if current > RATE_LIMIT:
            logger.warning("Rate limit exceeded", extra={
                "ip": client_ip, 
                "count": current
            })
            raise HTTPException(
                status_code=429, 
                detail="Too many requests"
            )

    except Exception as e:
        logger.error("Rate limiting failed (fail-open)", extra={
            "ip": client_ip, 
            "error": str(e)
        })
