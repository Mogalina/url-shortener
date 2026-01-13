import logging
from fastapi import APIRouter
from app.services.shortener import create_short_url

router = APIRouter()
logger = logging.getLogger("api.shorten")

@router.post("/shorten")
def shorten_url(long_url: str, ttl_days: int = 30):
    logger.info("Shorten request received")

    code = create_short_url(long_url, ttl_days)

    logger.info("Short URL created", extra={"code": code})
    return {"short_url": f"/{code}"}
