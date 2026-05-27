from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter(tags=["Health"])

@router.get("/")
def root():
    return {"service": settings.APP_NAME, "version": settings.VERSION, "status": "running"}

@router.get("/health")
def health():
    return {"status": "ok"}