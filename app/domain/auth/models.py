"""
Модели пользователя (домен Auth).

User — учётная запись (аутентификация: email, пароль, провайдер).
UserProfile вынесен отдельно (1:1), чтобы не раздувать таблицу
auth-данными вперемешку с публичным профилем (раздел 5.1
документации) — это разные зоны ответственности и разная частота
изменений: auth-поля почти не меняются, профиль меняется часто
(аватар, ник, XP, уровень).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AuthProvider, CEFRLevel
from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        default=AuthProvider.PASSWORD, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"


class UserProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Публичный профиль (раздел 5.1): аватар, ник, текущий CEFR-уровень."""

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    current_cefr_level: Mapped[CEFRLevel] = mapped_column(default=CEFRLevel.A1, nullable=False)

    # Раздел 4.2: уровень аккаунта — отдельная сущность от CEFR, растёт от XP.
    account_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_profile_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="profile")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserProfile user_id={self.user_id} nickname={self.nickname!r}>"
