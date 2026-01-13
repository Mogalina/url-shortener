import logging
from fastapi import FastAPI, Request
from app.api.v1.router import router
from app.core.logging import setup_logging
from app.core.security import rate_limit

setup_logging()
logger = logging.getLogger("api")

app = FastAPI(title="URL Shortener", version="1.0.0")

@app.middleware("http")
async def request_rate_limit(request: Request, call_next):
    logger.info("Incoming request", extra={
        "method": request.method,
        "path": request.url.path
    })

    rate_limit(request)
    response = await call_next(request)

    logger.info("Request completed", extra={
        "status_code": response.status_code
    })

    return response

app.include_router(router, prefix="/api/v1")
