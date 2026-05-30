"""Authentication endpoints."""

import structlog
from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DatabaseDep
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.services.auth import AuthService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DatabaseDep) -> UserResponse:
    """Register a new user."""
    user_repo = UserRepository(db)

    # Check if email exists
    existing = await user_repo.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    auth_service = AuthService()
    password_hash = auth_service.hash_password(request.password)

    user = await user_repo.create(
        email=request.email,
        password_hash=password_hash,
        full_name=request.full_name,
    )

    logger.info("User registered", user_id=user.id, email=user.email)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DatabaseDep) -> TokenResponse:
    """Login and receive access/refresh tokens."""
    user_repo = UserRepository(db)
    auth_service = AuthService()

    # Find user
    user = await user_repo.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Generate tokens
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    logger.info("User logged in", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth_service.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: DatabaseDep) -> TokenResponse:
    """Refresh access token using refresh token."""
    auth_service = AuthService()

    # Verify refresh token
    payload = auth_service.verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify user still exists and is active
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload.get("sub"))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Generate new tokens
    access_token = auth_service.create_access_token(user.id)
    new_refresh_token = auth_service.create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=auth_service.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    current_user: CurrentUser,
    db: DatabaseDep,
) -> UserResponse:
    """Update current user information."""
    user_repo = UserRepository(db)

    update_data = request.model_dump(exclude_unset=True)
    user = await user_repo.update(current_user.id, **update_data)

    return UserResponse.model_validate(user)
