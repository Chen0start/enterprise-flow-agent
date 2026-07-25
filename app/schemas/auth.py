from typing import Literal

from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    """Response returned after successful authentication."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
