"""
SatyaKavach - Audit Log Model
Immutable audit trail for all verification and security events
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text, JSON, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # BigInteger PKs don't autoincrement on SQLite — use INTEGER there (same behaviour on PostgreSQL)
    log_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    media_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    # 'metadata' is reserved by SQLAlchemy Declarative — map same DB column under a safe name
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
