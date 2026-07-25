from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Database access operations for users."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        """Find a user by primary key."""

        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """Find a user by normalized email address."""

        statement = select(User).where(User.email == email)

        return db.scalar(statement)

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        """Find a user by normalized username."""

        statement = select(User).where(User.username == username)

        return db.scalar(statement)

    @staticmethod
    def list_users(
        db: Session,
        *,
        skip: int,
        limit: int,
    ) -> list[User]:
        """Return users using offset pagination."""

        statement = select(User).order_by(User.id).offset(skip).limit(limit)

        return list(db.scalars(statement).all())

    @staticmethod
    def count_users(db: Session) -> int:
        """Return the total number of users."""

        statement = select(func.count(User.id))

        return db.scalar(statement) or 0

    @staticmethod
    def add(db: Session, user: User) -> User:
        """Add a user to the current transaction."""

        db.add(user)
        db.flush()

        return user
