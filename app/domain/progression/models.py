"""
Модели ядра прогрессии (раздел 1 документации).

Иерархия контента: CEFRLevel -> Section -> Unit -> Lesson.
Section.prerequisite_section_id задаёт явную смысловую зависимость между
разделами (раздел 1.2): если prerequisite не задан, раздел доступен сразу
при открытии своего CEFR-уровня — это и даёт "частичную параллельность"
(два раздела без зависимости друг от друга открыты одновременно).

Lesson.is_unit_checkpoint помечает контрольный урок юнита — его
прохождение обязательно для открытия следующего юнита (раздел 1.2).
Lesson.is_level_checkpoint помечает финальный тест уровня — его
прохождение открывает следующий CEFR-уровень.

User*Progress-таблицы хранят персональный прогресс отдельно от
контент-справочников (Section/Unit/Lesson) по той же логике, что и
UserKnowledgeState в domain/srs: контент общий, прогресс — персональный.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CEFRLevel, LessonType, ProgressStatus
from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Section(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Крупный раздел внутри CEFR-уровня (раздел 1.1)."""

    __tablename__ = "sections"

    cefr_level: Mapped[CEFRLevel] = mapped_column(nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Явная смысловая зависимость (раздел 1.2). NULL = доступен сразу
    # при открытии уровня — это и обеспечивает частичную параллельность.
    prerequisite_section_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="SET NULL"), nullable=True
    )

    units: Mapped[list["Unit"]] = relationship(
        back_populates="section", order_by="Unit.order_index", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("cefr_level", "order_index", name="uq_section_level_order"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Section {self.code} level={self.cefr_level}>"


class Unit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Юнит внутри раздела (раздел 1.1)."""

    __tablename__ = "units"

    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    section: Mapped["Section"] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", order_by="Lesson.order_index", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("section_id", "order_index", name="uq_unit_section_order"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Unit {self.code} section_id={self.section_id}>"


class Lesson(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Урок внутри юнита (раздел 1.1, 1.3)."""

    __tablename__ = "lessons"

    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    lesson_type: Mapped[LessonType] = mapped_column(nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Раздел 1.3: ровно одна заявленная обучающая цель на урок.
    learning_goal: Mapped[str] = mapped_column(String(255), nullable=False)

    xp_reward: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Раздел 1.2: контрольный урок юнита обязателен для открытия следующего юнита.
    is_unit_checkpoint: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Раздел 1.2: финальный тест уровня открывает следующий CEFR-уровень.
    is_level_checkpoint: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    unit: Mapped["Unit"] = relationship(back_populates="lessons")

    __table_args__ = (
        UniqueConstraint("unit_id", "order_index", name="uq_lesson_unit_order"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Lesson {self.title!r} type={self.lesson_type}>"


class UserLevelProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Прогресс пользователя по CEFR-уровню в целом."""

    __tablename__ = "user_level_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    cefr_level: Mapped[CEFRLevel] = mapped_column(nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(default=ProgressStatus.LOCKED, nullable=False)

    unlocked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "cefr_level", name="uq_user_level_progress_identity"),
    )


class UserSectionProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Прогресс пользователя по разделу."""

    __tablename__ = "user_section_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ProgressStatus] = mapped_column(default=ProgressStatus.LOCKED, nullable=False)

    unlocked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "section_id", name="uq_user_section_progress_identity"),
    )


class UserUnitProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Прогресс пользователя по юниту."""

    __tablename__ = "user_unit_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ProgressStatus] = mapped_column(default=ProgressStatus.LOCKED, nullable=False)

    unlocked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "unit_id", name="uq_user_unit_progress_identity"),
    )


class UserLessonProgress(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Прогресс пользователя по конкретному уроку."""

    __tablename__ = "user_lesson_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ProgressStatus] = mapped_column(default=ProgressStatus.LOCKED, nullable=False)

    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_without_mistakes: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    unlocked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress_identity"),
    )
