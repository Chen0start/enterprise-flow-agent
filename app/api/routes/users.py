from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_admin,
)
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserRead,
    UserRole,
)
from app.services.user import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    _current_admin: Annotated[
        User,
        Depends(require_admin),
    ],
) -> User:
    """Create a user. Administrator permission is required."""

    try:
        return UserService.create_user(
            db,
            payload,
        )

    except ResourceConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=UserListResponse,
)
def list_users(
    _current_admin: Annotated[
        User,
        Depends(require_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    skip: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
) -> UserListResponse:
    """Return a paginated user list for administrators."""

    users, total = UserService.list_users(
        db,
        skip=skip,
        limit=limit,
    )

    return UserListResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/me",
    response_model=UserRead,
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    """Return the currently authenticated user."""

    return current_user


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:
    """Return one user to an administrator or the user themself."""

    is_admin = current_user.role == UserRole.ADMIN.value

    is_self = current_user.id == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this user",
        )

    try:
        return UserService.get_user(
            db,
            user_id,
        )

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
