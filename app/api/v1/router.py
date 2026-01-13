from fastapi import APIRouter
from app.api.v1.endpoints import shorten, redirect

router = APIRouter()
router.include_router(shorten.router, tags=["shorten"])
router.include_router(redirect.router, tags=["redirect"])
