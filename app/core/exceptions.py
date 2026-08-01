"""
Доменные исключения.

Важный принцип: бизнес-логика (domain/) никогда не бросает HTTPException
и ничего не знает про FastAPI. Она бросает эти доменные исключения.
Перевод в HTTP-ответ происходит централизованно в
app.api.error_handlers — это даёт: (1) переиспользуемость сервисов вне
HTTP-контекста (воркеры, CLI, тесты), (2) единый формат ошибок API.
"""
from __future__ import annotations


class AppError(Exception):
    """Базовый класс всех доменных ошибок приложения."""

    code: str = "app_error"
    http_status: int = 500
    message: str = "Внутренняя ошибка приложения"

    def __init__(self, message: str | None = None, **context: object) -> None:
        self.message = message or self.message
        self.context = context
        super().__init__(self.message)


class NotFoundError(AppError):
    code = "not_found"
    http_status = 404
    message = "Запрашиваемый объект не найден"


class AlreadyExistsError(AppError):
    code = "already_exists"
    http_status = 409
    message = "Объект уже существует"


class ValidationError(AppError):
    code = "validation_error"
    http_status = 422
    message = "Ошибка валидации данных"


class AuthenticationError(AppError):
    code = "authentication_error"
    http_status = 401
    message = "Ошибка аутентификации"


class InvalidCredentialsError(AuthenticationError):
    code = "invalid_credentials"
    message = "Неверный email или пароль"


class TokenExpiredError(AuthenticationError):
    code = "token_expired"
    message = "Токен истёк"


class TokenInvalidError(AuthenticationError):
    code = "token_invalid"
    message = "Недействительный токен"


class AuthorizationError(AppError):
    code = "authorization_error"
    http_status = 403
    message = "Недостаточно прав для выполнения действия"


class RateLimitExceededError(AppError):
    code = "rate_limit_exceeded"
    http_status = 429
    message = "Превышен лимит запросов"


class ExternalServiceError(AppError):
    """Ошибка при обращении к внешнему сервису (DeepSeek API и т.п.)."""

    code = "external_service_error"
    http_status = 502
    message = "Внешний сервис временно недоступен"


class ConflictStateError(AppError):
    """Действие невозможно из-за текущего состояния сущности."""

    code = "conflict_state"
    http_status = 409
    message = "Действие невозможно в текущем состоянии"


class UserNotFoundError(NotFoundError):
    code = "user_not_found"
    message = "Пользователь не найден"


class EmailAlreadyRegisteredError(AlreadyExistsError):
    code = "email_already_registered"
    message = "Пользователь с таким email уже зарегистрирован"


class NicknameAlreadyTakenError(AlreadyExistsError):
    code = "nickname_already_taken"
    message = "Этот никнейм уже занят"


class InactiveUserError(AuthenticationError):
    code = "inactive_user"
    message = "Учётная запись деактивирована"


# --- Progression (раздел 1 документации) ---


class SectionNotFoundError(NotFoundError):
    code = "section_not_found"
    message = "Раздел не найден"


class UnitNotFoundError(NotFoundError):
    code = "unit_not_found"
    message = "Юнит не найден"


class LessonNotFoundError(NotFoundError):
    code = "lesson_not_found"
    message = "Урок не найден"


class SectionLockedError(ConflictStateError):
    code = "section_locked"
    message = "Раздел ещё не открыт"


class UnitLockedError(ConflictStateError):
    code = "unit_locked"
    message = "Юнит ещё не открыт"


class LessonLockedError(ConflictStateError):
    code = "lesson_locked"
    message = "Урок ещё не открыт"


# --- SRS (раздел 3 документации) ---


class KnowledgeItemNotFoundError(NotFoundError):
    code = "knowledge_item_not_found"
    message = "Единица знания не найдена"


# --- Gamification (раздел 4, 6 документации) ---


class DailyQuestNotFoundError(NotFoundError):
    code = "daily_quest_not_found"
    message = "Ежедневное задание не найдено"
