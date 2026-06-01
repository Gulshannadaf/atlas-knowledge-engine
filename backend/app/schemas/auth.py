"""Authentication schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class UserResponse(BaseSchema):
    """User response schema."""

    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    """User update request schema."""

    full_name: str | None = Field(default=None, max_length=255)
    settings: dict | None = None
