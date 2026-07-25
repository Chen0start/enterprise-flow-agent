from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(StrEnum):
    """Roles supported by the first application version."""

    EMPLOYEE = "employee"
    PROJECT_MANAGER = "project_manager"
    ADMIN = "admin"


class UserCreate(BaseModel):
    """Request body for creating a user."""

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-z0-9_.-]+$",
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: UserRole = UserRole.EMPLOYEE

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        """Strip whitespace and store usernames in lowercase."""

        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        """Strip whitespace and normalize email addresses."""

        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Require at least one letter and one number."""

        has_letter = any(character.isalpha() for character in value)
        has_number = any(character.isdigit() for character in value)

        if not has_letter or not has_number:
            raise ValueError("Password must contain at least one letter and one number")

        return value


class UserRead(BaseModel):
    """Public user information returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserRead]
    total: int
    skip: int
    limit: int
