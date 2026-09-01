"""
SatyaKavach - Authentication API
Registration, login, anonymous sessions, token refresh
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, AnonymousSession
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check existing
    if data.email:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

    if data.phone_number:
        existing = await db.execute(select(User).where(User.phone_number == data.phone_number))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone number already registered")

    user = User(
        email=data.email,
        phone_number=data.phone_number,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        preferred_language=data.preferred_language,
        role="citizen",
        is_anonymous=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": user.user_id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email/phone and password."""
    query = select(User).where(
        or_(User.email == data.email, User.phone_number == data.phone_number)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_active_at = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token({"sub": user.user_id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/anonymous", response_model=AnonymousSession)
async def create_anonymous_session(db: AsyncSession = Depends(get_db)):
    """Create an anonymous session for verification without an account."""
    user = User(
        is_anonymous=True,
        role="citizen",
        preferred_language="hi",
        full_name="Anonymous User",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.user_id, "role": user.role, "anonymous": True})

    return AnonymousSession(
        user_id=user.user_id,
        token=token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Get new access token from refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": user.user_id, "role": user.role})
    new_refresh = create_refresh_token({"sub": user.user_id})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """Get current user info."""
    return UserResponse.model_validate(user)
