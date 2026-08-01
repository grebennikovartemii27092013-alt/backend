"""
Доменные перечисления, разделяемые между несколькими доменами.

CEFRLevel соответствует разделу 1.1 документации: A1 -> A2 -> B1 -> B2 -> C1 -> C2.
Лежит на уровне app.domain (а не внутри domain/auth), т.к. используется
не только профилем пользователя, но и progression/lessons в дальнейшем.
"""
from __future__ import annotations

import enum


class CEFRLevel(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    @property
    def order(self) -> int:
        """Порядковый номер уровня для сравнений (A1 < A2 < ... < C2)."""
        return list(CEFRLevel).index(self)


class AuthProvider(str, enum.Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    APPLE = "apple"


class KnowledgeItemType(str, enum.Enum):
    """Тип единицы знания для SRS (раздел 3.2 документации)."""

    WORD = "word"
    PHRASE = "phrase"
    GRAMMAR_RULE = "grammar_rule"


class LessonType(str, enum.Enum):
    """Функциональный тип урока внутри юнита (раздел 1.1 документации)."""

    NEW_MATERIAL = "new_material"
    REINFORCEMENT = "reinforcement"
    MIXED_PRACTICE = "mixed_practice"
    CHECKPOINT = "checkpoint"
    AI_DIALOGUE = "ai_dialogue"


class ProgressStatus(str, enum.Enum):
    """Статус прохождения сущности прогрессии (уровень/раздел/юнит/урок)."""

    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class XPSourceType(str, enum.Enum):
    """Источник начисления XP (раздел 4.1 документации)."""

    LESSON_COMPLETE = "lesson_complete"
    LESSON_NO_MISTAKES_BONUS = "lesson_no_mistakes_bonus"
    DAILY_QUEST = "daily_quest"
    REVIEW_SESSION = "review_session"
    DAILY_LOGIN_STREAK = "daily_login_streak"
    SOCIAL_ROOM_LESSON = "social_room_lesson"
    COOP_GAME = "coop_game"


class DailyQuestTargetType(str, enum.Enum):
    """Тип цели ежедневного задания (раздел 6.1 документации)."""

    LESSONS_COMPLETED = "lessons_completed"
    XP_EARNED = "xp_earned"
    LESSON_NO_MISTAKES = "lesson_no_mistakes"
    WORDS_REVIEWED = "words_reviewed"

