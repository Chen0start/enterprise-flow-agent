from datetime import date, datetime
from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ProjectStatus(StrEnum):
    """Lifecycle states supported by a project."""

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectRole(StrEnum):
    """Roles held by users inside a project."""

    OWNER = "owner"
    MANAGER = "manager"
    MEMBER = "member"


class AssignableProjectRole(StrEnum):
    """Project roles that may be assigned to new members."""

    MANAGER = "manager"
    MEMBER = "member"


class ProjectCreate(BaseModel):
    """Request body for creating a project."""

    name: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    status: ProjectStatus = ProjectStatus.PLANNED

    start_date: date | None = None
    planned_end_date: date | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        """Remove surrounding whitespace from a project name."""

        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(
        cls,
        value: object,
    ) -> object:
        """Normalize an optional project description."""

        if isinstance(value, str):
            normalized = value.strip()

            return normalized or None

        return value

    @model_validator(mode="after")
    def validate_project(self) -> Self:
        """Validate project dates and initial status."""

        if (
            self.start_date is not None
            and self.planned_end_date is not None
            and self.planned_end_date < self.start_date
        ):
            raise ValueError("Planned end date cannot be earlier than start date")

        if self.status in {
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        }:
            raise ValueError("A new project must be planned or active")

        return self


class ProjectRead(BaseModel):
    """Project information returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    description: str | None
    status: ProjectStatus
    owner_id: int
    created_by_id: int
    start_date: date | None
    planned_end_date: date | None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Paginated project list."""

    items: list[ProjectRead]
    total: int
    skip: int
    limit: int


class ProjectMemberAdd(BaseModel):
    """Request for adding one user to a project."""

    user_id: int = Field(gt=0)

    project_role: AssignableProjectRole = AssignableProjectRole.MEMBER


class ProjectMemberRead(BaseModel):
    """Project membership returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    project_id: int
    user_id: int
    project_role: ProjectRole
    joined_at: datetime


class ProjectMemberListResponse(BaseModel):
    """Project member list response."""

    items: list[ProjectMemberRead]
    total: int
