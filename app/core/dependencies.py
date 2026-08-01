"""Переиспользуемые FastAPI dependencies."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, decode_token
from app.domain.auth.models import User
from app.domain.auth.service import AuthService
from app.infrastructure.db.session import get_db_session

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    session: DbSession,
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> User:
    user_id = decode_token(token, expected_type=TokenType.ACCESS)
    service = AuthService(session)
    return await service.get_user_by_id(user_id)


CurrentUser = Annotated[User, Depends(get_current_user)]
