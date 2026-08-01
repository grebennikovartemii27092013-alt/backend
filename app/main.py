"""Точка входа FastAPI-приложения."""

from __future__ import annotations

import subprocess
from pathlib import Path
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


def run_migrations():
    """
    Запуск alembic миграций.
    Работает и локально, и на Render.
    """

    try:
        # english-app-complete/
        # ├── alembic.ini
        # └── backend/
        #     └── app/
        #         └── main.py

        project_root = Path(__file__).resolve().parents[2]

        alembic_file = project_root / "alembic.ini"

        if not alembic_file.exists():
            logger.warning(
                "alembic_not_found",
                path=str(alembic_file)
            )
            return

        subprocess.run(
            [
                "alembic",
                "-c",
                str(alembic_file),
                "upgrade",
                "head",
            ],
            cwd=str(project_root),
            check=True,
        )

        logger.info("migration_success")

    except Exception as e:
        logger.error(
            "migration_failed",
            error=str(e)
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()

    run_migrations()

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


    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://clever-dusk-364fcc.netlify.app",
            "https://cosmic-mandazi-cf5cc1.netlify.app",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    register_error_handlers(app)

    app.include_router(
        api_router,
        prefix=settings.api_prefix,
    )


    @app.get("/health", tags=["system"])
    async def health():
        return {
            "status": "ok"
        }


    return app


app = create_app()