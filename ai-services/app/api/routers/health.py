"""AgroVision AI — Router health."""
from __future__ import annotations

from fastapi import APIRouter

from app.config.settings import get_settings
from app.ml.inference.predictor import model_is_trained
from app.utils.dates import utcnow_iso

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    s = get_settings()
    return {
        "status":        "ok",
        "app":           s.app_name,
        "env":           s.env,
        "model_trained": model_is_trained(),
        "timestamp":     utcnow_iso(),
    }
