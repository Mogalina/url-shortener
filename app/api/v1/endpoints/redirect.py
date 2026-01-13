import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.services.resolver import resolve_url

router = APIRouter()
logger = logging.getLogger("api.redirect")

@router.get("/{code}")
def redirect(code: str):
    logger.info("Redirect request", extra={"code": code})

    url = resolve_url(code)
    if not url:
        logger.warning("Short code not found", extra={"code": code})
        raise HTTPException(status_code=404)

    logger.info("Redirecting", extra={"code": code})
    return RedirectResponse(url)
