from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationError,
    InactiveUserError,
)
from app.core.security import verify_password
from app.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    """Authentication-related business logic."""

    @staticmethod
    def authenticate_user(
        db: Session,
        *,
        login: str,
        password: str,
    ) -> User:
        """Authenticate a user by username or email."""

        user = UserRepository.get_by_login(
            db,
            login,
        )

        if user is None:
            raise AuthenticationError("Incorrect username or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise AuthenticationError("Incorrect username or password")

        if not user.is_active:
            raise InactiveUserError("User account is inactive")

        return user
