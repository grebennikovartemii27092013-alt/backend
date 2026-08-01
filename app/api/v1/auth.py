from passlib.context import CryptContext

# bcrypt через passlib
_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Создание хеша пароля.
    bcrypt имеет лимит 72 байта,
    поэтому обрезаем безопасно.
    """
    if not isinstance(password, str):
        password = str(password)

    password = password.strip()

    # bcrypt максимум 72 байта
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        password = password_bytes[:72].decode(
            "utf-8",
            errors="ignore"
        )

    return _pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Проверка пароля.
    """

    if not isinstance(plain_password, str):
        plain_password = str(plain_password)

    plain_password = plain_password.strip()

    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode(
            "utf-8",
            errors="ignore"
        )

    return _pwd_context.verify(
        plain_password,
        hashed_password
    )