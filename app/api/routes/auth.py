from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    InactiveUserError,
)
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import AccessTokenResponse
from app.services.auth import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/login",
    response_model=AccessTokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> AccessTokenResponse:
    """Authenticate a user and return a JWT access token."""

    try:
        user = AuthService.authenticate_user(
            db,
            login=form_data.username,
            password=form_data.password,
        )

    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    settings = get_settings()

    token = create_access_token(
        subject=user.id,
    )

    return AccessTokenResponse(
        access_token=token,
        expires_in=(settings.access_token_expire_minutes * 60),
    )
