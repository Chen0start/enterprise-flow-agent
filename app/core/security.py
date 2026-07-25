from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password before database storage."""

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against a stored hash."""

    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for one user."""

    settings = get_settings()
    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expires_at = now + expires_delta

    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> int:
    """Decode a JWT access token and return its user ID."""

    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                ],
            },
        )

    except InvalidTokenError as exc:
        raise ValueError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    subject = payload.get("sub")

    try:
        user_id = int(subject)

    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid token subject") from exc

    if user_id <= 0:
        raise ValueError("Invalid token subject")

    return user_id
