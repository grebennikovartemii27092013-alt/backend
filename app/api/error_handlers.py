"""
Единая точка перевода исключений в HTTP-ответы.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.logging import get_logger


logger = get_logger(__name__)


def _error_payload(
    code: str,
    message: str,
    context: dict | None = None
) -> dict:
    payload = {
        "error": {
            "code": code,
            "message": message,
        }
    }

    if context:
        payload["error"]["context"] = context

    return payload


async def app_error_handler(
    request: Request,
    exc: AppError
) -> JSONResponse:

    logger.info(
        "app_error_handled",
        path=request.url.path,
        error_code=exc.code,
    )

    return JSONResponse(
        status_code=exc.http_status,
        content=_error_payload(
            exc.code,
            exc.message,
            exc.context
        ),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:

    logger.info(
        "request_validation_failed",
        path=request.url.path,
        errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload(
            "validation_error",
            "Ошибка валидации запроса",
            {
                "details": exc.errors()
            },
        ),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:

    logger.error(
        "unhandled_exception",
        path=request.url.path,
        exc_info=exc
    )

    return JSONResponse(
        status_code=500,
        content=_error_payload(
            "internal_error",
            "Внутренняя ошибка сервера"
        ),
    )


def register_error_handlers(app: FastAPI) -> None:

    app.add_exception_handler(
        AppError,
        app_error_handler
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler
    )