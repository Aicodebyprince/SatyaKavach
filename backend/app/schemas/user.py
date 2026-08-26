"""
SatyaKavach - User Schemas (Pydantic models)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    preferred_language: str = "hi"


class UserLogin(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    preferred_language: str
    role: str
    is_anonymous: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class AnonymousSession(BaseModel):
    user_id: str
    token: str
    token_type: str = "bearer"
