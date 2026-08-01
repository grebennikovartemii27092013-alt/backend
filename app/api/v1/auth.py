"""HTTP-слой Auth-домена."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.domain.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)
from app.domain.auth.service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    session: DbSession,
) -> TokenPairResponse:
    service = AuthService(session)

    user = await service.register(data)

    return await service.issue_token_pair(user.id)


@router.post(
    "/login",
    response_model=TokenPairResponse,
)
async def login(
    data: LoginRequest,
    session: DbSession,
) -> TokenPairResponse:
    service = AuthService(session)

    user = await service.authenticate(
        data.email,
        data.password,
    )

    return await service.issue_token_pair(user.id)


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
)
async def refresh(
    data: RefreshRequest,
    session: DbSession,
) -> TokenPairResponse:
    service = AuthService(session)

    return await service.refresh_tokens(
        data.refresh_token
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(user)