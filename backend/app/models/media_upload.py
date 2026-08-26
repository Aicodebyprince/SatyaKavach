"""
SatyaKavach - Media Upload Model
Tracks uploaded media through the verification pipeline
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MediaUpload(Base):
    __tablename__ = "media_uploads"

    media_id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=True, index=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # image, video, audio, link, screenshot
    channel: Mapped[str] = mapped_column(String(20), default="web")  # web, pwa, voice, message
    original_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # Deduplication
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="queued", index=True
    )  # queued, preprocessing, analyzing, scoring, complete, failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="media_uploads")
    verification = relationship("VerificationRecord", back_populates="media", uselist=False)
