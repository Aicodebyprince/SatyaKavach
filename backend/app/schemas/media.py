"""
SatyaKavach - Media Upload & Verification Schemas
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class MediaUploadResponse(BaseModel):
    media_id: str
    media_type: str
    status: str
    message: str
    created_at: datetime


class LinkSubmitRequest(BaseModel):
    url: str = Field(..., description="URL/link to verify")
    language: Optional[str] = None


class VerificationStatusResponse(BaseModel):
    media_id: str
    status: str
    progress: str  # Human-readable progress message
    trust_score: Optional[int] = None
    verdict: Optional[str] = None


class ModelBreakdown(BaseModel):
    signal_name: str
    model_name: str
    score: float
    available: bool = True


class TrustScoreResult(BaseModel):
    record_id: str
    media_id: str
    media_type: str
    trust_score: int = Field(..., ge=0, le=100)
    verdict: str  # HIGH_TRUST, UNCERTAIN, LOW_TRUST
    recommended_action: str
    model_breakdown: dict[str, Any]
    evidence_report: dict[str, Any]
    confidence: Optional[float] = None
    analysis_duration_ms: Optional[int] = None
    created_at: datetime


class VerificationHistoryResponse(BaseModel):
    records: list[TrustScoreResult]
    total: int
    page: int
    page_size: int
