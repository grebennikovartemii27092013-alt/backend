"""Точка входа FastAPI-приложения."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.db.session import engine


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()

    logger.info(
        "app_startup",
        environment=settings.environment
    )

    yield

    await engine.dispose()

    logger.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS для Netlify + локальной разработки
    allowed_origins = [
        "https://clever-dusk-364fcc.netlify.app",
        "https://cosmic-mandazi-cf5cc1.netlify.app",
        "http://localhost:3000",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
    ]

    # если в Render есть переменная CORS_ALLOW_ORIGINS
    # добавляем её тоже
    try:
        if settings.cors_allow_origins:
            allowed_origins.extend(settings.cors_allow_origins)
    except Exception:
        pass


    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(set(allowed_origins)),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    register_error_handlers(app)


    app.include_router(
        api_router,
        prefix=settings.api_prefix
    )


    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok"
        }


    return app


app = create_app()