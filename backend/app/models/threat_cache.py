"""
SatyaKavach - Threat Intelligence Cache Model
Caches URL/domain reputation results with TTL
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Numeric, JSON, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ThreatCache(Base):
    __tablename__ = "threat_intel_cache"

    # BigInteger PKs don't autoincrement on SQLite — use INTEGER there (same behaviour on PostgreSQL)
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    target: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)  # url, domain, file_hash
    threat_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    vendor_verdicts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
