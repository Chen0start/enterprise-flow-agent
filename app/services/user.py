from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """Business logic for user management."""

    @staticmethod
    def create_user(
        db: Session,
        payload: UserCreate,
    ) -> User:
        """Validate and create a user."""

        normalized_email = str(payload.email)

        if UserRepository.get_by_email(db, normalized_email) is not None:
            raise ResourceConflictError("A user with this email already exists")

        if UserRepository.get_by_username(db, payload.username) is not None:
            raise ResourceConflictError("A user with this username already exists")

        user = User(
            username=payload.username,
            email=normalized_email,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
            is_active=True,
        )

        try:
            UserRepository.add(db, user)
            db.commit()
            db.refresh(user)

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictError("Username or email already exists") from exc

        return user

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
    ) -> User:
        """Return a user or raise a not-found error."""

        user = UserRepository.get_by_id(db, user_id)

        if user is None:
            raise ResourceNotFoundError(f"User {user_id} was not found")

        return user

    @staticmethod
    def list_users(
        db: Session,
        *,
        skip: int,
        limit: int,
    ) -> tuple[list[User], int]:
        """Return users and the total user count."""

        users = UserRepository.list_users(
            db,
            skip=skip,
            limit=limit,
        )

        total = UserRepository.count_users(db)

        return users, total
