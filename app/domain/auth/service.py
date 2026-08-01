"""
Бизнес-логика Auth-домена.

AuthService ничего не знает про FastAPI/HTTP — принимает и возвращает
только ORM-модели и примитивы, бросает доменные исключения.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    NicknameAlreadyTakenError,
    UserNotFoundError,
)

from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

from app.domain.auth.models import User, UserProfile
from app.domain.auth.schemas import RegisterRequest, TokenPairResponse
from app.domain.enums import AuthProvider


class AuthService:
    """Сервис аутентификации."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == email)
        )

        return result.scalar_one_or_none()


    async def _nickname_taken(self, nickname: str) -> bool:
        result = await self._session.execute(
            select(UserProfile.id)
            .where(UserProfile.nickname == nickname)
        )

        return result.scalar_one_or_none() is not None


    async def register(self, data: RegisterRequest) -> User:
        """Создание пользователя и профиля."""

        if await self._get_user_by_email(data.email):
            raise EmailAlreadyRegisteredError()


        if await self._nickname_taken(data.nickname):
            raise NicknameAlreadyTakenError()


        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            auth_provider=AuthProvider.PASSWORD,
        )


        user.profile = UserProfile(
            nickname=data.nickname
        )


        self._session.add(user)

        await self._session.flush()

        await self._session.refresh(
            user,
            attribute_names=["profile"]
        )

        return user



    async def authenticate(
        self,
        email: str,
        password: str
    ) -> User:

        user = await self._get_user_by_email(email)


        if user is None or user.hashed_password is None:
            raise InvalidCredentialsError()


        if not verify_password(
            password,
            user.hashed_password
        ):
            raise InvalidCredentialsError()


        if not user.is_active:
            raise InactiveUserError()


        return user



    async def issue_token_pair(
        self,
        user_id: uuid.UUID
    ) -> TokenPairResponse:

        return TokenPairResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )



    async def refresh_tokens(
        self,
        refresh_token: str
    ) -> TokenPairResponse:

        user_id = decode_token(
            refresh_token,
            expected_type=TokenType.REFRESH
        )


        user = await self.get_user_by_id(user_id)


        if not user.is_active:
            raise InactiveUserError()


        return await self.issue_token_pair(user.id)



    async def get_user_by_id(
        self,
        user_id: uuid.UUID
    ) -> User:

        result = await self._session.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )


        user = result.scalar_one_or_none()


        if user is None:
            raise UserNotFoundError()


        return user