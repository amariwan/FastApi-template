from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_app_settings, get_db_settings
from .core.core_api.advanced_v1 import router as advanced_v1_router
from .core.core_api.config_v1 import router as config_v1_router
from .core.core_api.public_v1 import router as public_v1_router
from .core.core_api.templates_v1 import router as templates_v1_router
from .core.core_db.async_db_session_maker import get_sessionmanager
from .core.core_middleware.profiler_middleware import register_profiling_middleware

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Handle startup/shutdown for the FastAPI app."""
    app_settings = get_app_settings()
    db_settings = get_db_settings()

    print(f"Starting app with LOG_LEVEL {app_settings.LOG_LEVEL.value}")
    if db_settings.DB_ENABLED:
        print(f"Connecting to DB={db_settings.DB_DATABASE} on port {db_settings.DB_PORT}")
    else:
        print("Database disabled - not connecting to DB")

    yield

    if db_settings.DB_ENABLED:
        session_manager = get_sessionmanager()
        if session_manager.engine is not None:
            await session_manager.close()

    print("Shutting down server and cleaning up resources")


def create_app() -> FastAPI:
    app_settings = get_app_settings()

    new_app_instance = FastAPI(title=app_settings.APP_TITLE, lifespan=lifespan)

    cors_list = app_settings.cors_allowed_origins

    # Optional override for local demo servers when DEMO_CORS_ORIGINS env var is set
    # Example: DEMO_CORS_ORIGINS="http://127.0.0.1:5500" or "*"
    demo_cors_env = os.environ.get("DEMO_CORS_ORIGINS")
    if demo_cors_env:
        if demo_cors_env.strip() == "*":
            cors_list = ["*"]
        else:
            cors_list = [o.strip() for o in demo_cors_env.split(",") if o.strip()]

    if cors_list:
        new_app_instance.add_middleware(
            CORSMiddleware,
            allow_origins=cors_list,
            allow_credentials=True,
            allow_methods=app_settings.cors_allow_methods,
            allow_headers=app_settings.cors_allow_headers,
        )

    new_app_instance.include_router(public_v1_router)

    for router in (templates_v1_router, config_v1_router, advanced_v1_router):
        new_app_instance.include_router(router, prefix=app_settings.API_PREFIX)

    demo_dir = Path(__file__).resolve().parents[3] / "static" / "demo"
    if demo_dir.exists():
        new_app_instance.mount("/demo", StaticFiles(directory=str(demo_dir)), name="demo")

    register_profiling_middleware(new_app_instance, profiling_enabled=app_settings.PROFILING_ENABLED)

    return new_app_instance


app = create_app()
