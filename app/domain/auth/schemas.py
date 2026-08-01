"""
Pydantic-схемы для Auth API.

Схемы отделены от ORM-моделей (app.domain.auth.models): это разные
контракты — модель описывает хранение, схема описывает то, что видит
клиент по HTTP. RegisterRequest сразу требует nickname, т.к. в системе
UserProfile создаётся синхронно с User (см. AuthService.register) —
профиль без ника существовать не может (раздел 5.1: ник обязателен
для соцчасти).
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.enums import CEFRLevel

_NICKNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,50}$")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=3, max_length=50)

    @field_validator("nickname")
    @classmethod
    def _validate_nickname(cls, v: str) -> str:
        if not _NICKNAME_RE.match(v):
            raise ValueError(
                "Никнейм может содержать только латинские буквы, цифры и подчёркивание (3-50 символов)"
            )
        return v

    @field_validator("password")
    @classmethod
    def _validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну букву и одну цифру")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nickname: str
    avatar_url: str | None
    current_cefr_level: CEFRLevel
    account_level: int
    total_xp: int
    is_profile_public: bool


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: UserProfileResponse
