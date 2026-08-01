"""Pydantic-схемы для Progression API (раздел 1 документации)."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import CEFRLevel, LessonType, ProgressStatus


class LevelStatusResponse(BaseModel):
    cefr_level: CEFRLevel
    status: ProgressStatus


class SectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cefr_level: CEFRLevel
    order_index: int
    code: str
    title: str
    description: str | None
    prerequisite_section_id: uuid.UUID | None
    status: ProgressStatus = ProgressStatus.LOCKED


class UnitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    section_id: uuid.UUID
    order_index: int
    code: str
    title: str
    description: str | None
    status: ProgressStatus = ProgressStatus.LOCKED


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    unit_id: uuid.UUID
    order_index: int
    lesson_type: LessonType
    title: str
    learning_goal: str
    xp_reward: int
    is_unit_checkpoint: bool
    is_level_checkpoint: bool
    status: ProgressStatus = ProgressStatus.LOCKED
    best_score: int = 0


class CompleteLessonRequest(BaseModel):
    score: int = Field(ge=0, le=100, description="Итоговый результат урока, 0-100")
    completed_without_mistakes: bool = False


class CompleteLessonResponse(BaseModel):
    lesson_id: uuid.UUID
    status: ProgressStatus
    best_score: int
    unit_completed: bool
    next_unit_unlocked: bool
    level_completed: bool
    next_level_unlocked: bool
    xp_awarded: int
