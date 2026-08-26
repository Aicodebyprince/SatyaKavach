"""
SatyaKavach - Verification Record Model
Stores the complete verification result for each analysis
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    record_id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("users.user_id"), nullable=True, index=True)
    media_id: Mapped[str] = mapped_column(String(50), ForeignKey("media_uploads.media_id"), unique=True, nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    trust_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    verdict: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # HIGH_TRUST, UNCERTAIN, LOW_TRUST
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    evidence_report: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    analysis_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = relationship("User", back_populates="verification_records")
    media = relationship("MediaUpload", back_populates="verification")
