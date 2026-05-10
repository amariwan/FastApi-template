from __future__ import annotations

from fastapi import APIRouter

from ...config import get_app_settings, get_db_settings

router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("", summary="Return a small runtime configuration snapshot")
def runtime_config() -> dict[str, object]:
    app_settings = get_app_settings()
    db_settings = get_db_settings()
    return {
        "app_title": app_settings.APP_TITLE,
        "api_prefix": app_settings.API_PREFIX,
        "log_level": app_settings.LOG_LEVEL.value,
        "db_enabled": db_settings.DB_ENABLED,
        "db_database": db_settings.DB_DATABASE,
    }