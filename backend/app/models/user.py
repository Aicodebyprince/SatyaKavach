"""
SatyaKavach - User Model
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(15), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="hi")
    role: Mapped[str] = mapped_column(String(20), default="citizen", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    media_uploads = relationship("MediaUpload", back_populates="user")
    verification_records = relationship("VerificationRecord", back_populates="user")
