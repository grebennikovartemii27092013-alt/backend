"""
Модели системы повторения (раздел 3 документации).

KnowledgeItem — минимальная единица (слово/фраза/грамматика).
UserKnowledgeState — персональное состояние пользователя по конкретному
KnowledgeItem: Strength (прочность), даты повторений. Разделены,
потому что KnowledgeItem — общий контент-справочник, а состояние —
персональные данные каждого пользователя по этому контенту (N:N через
собственный ключ, а не просто association table, т.к. несёт много
собственных полей).

Точные формулы интервалов (п. 3.4 документации) оставлены как numeric
policy — реализованы в app/services/srs.py, а не зашиты в модель.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import KnowledgeItemType


class KnowledgeItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Справочник обучаемых единиц: слово, фраза или грамматическое правило."""

    __tablename__ = "knowledge_items"

    item_type: Mapped[KnowledgeItemType] = mapped_column(nullable=False, index=True)

    # Каноничная форма (напр. "go" для слова, "Present Simple: negatives" для правила)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    translation: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # CEFR-уровень, на котором единица вводится впервые (для фильтрации контента)
    cefr_level: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("item_type", "content", "cefr_level", name="uq_knowledge_item_identity"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<KnowledgeItem {self.item_type}:{self.content!r}>"


class UserKnowledgeState(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Персональное состояние пользователя по KnowledgeItem.

    strength: 0.0-1.0, снижается со временем, растёт при успешном повторении
    (раздел 3.3). due_at: когда элемент должен быть предложен снова.
    """

    __tablename__ = "user_knowledge_states"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_items.id", ondelete="CASCADE"), nullable=False
    )

    strength: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    repetitions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)

    knowledge_item: Mapped["KnowledgeItem"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_item_id", name="uq_user_knowledge_state_identity"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserKnowledgeState user_id={self.user_id} item_id={self.knowledge_item_id} strength={self.strength:.2f}>"
