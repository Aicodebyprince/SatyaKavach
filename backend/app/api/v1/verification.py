"""
SatyaKavach - Verification Results API
Get results, poll status, view verification history
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.user import User
from app.models.media_upload import MediaUpload
from app.models.verification_record import VerificationRecord
from app.api.v1.deps import get_current_user, require_auth
from app.schemas.media import VerificationStatusResponse, TrustScoreResult, VerificationHistoryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/verification", tags=["Verification"])


@router.get("/{media_id}/status", response_model=VerificationStatusResponse)
async def get_verification_status(
    media_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Poll verification status for a media upload."""
    result = await db.execute(
        select(MediaUpload).where(MediaUpload.media_id == media_id)
    )
    media = result.scalar_one_or_none()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    progress_messages = {
        "queued": "Your media is in the queue for verification...",
        "preprocessing": "Preparing your media for analysis...",
        "analyzing": "Running AI detection models...",
        "scoring": "Computing trust score...",
        "complete": "Verification complete!",
        "failed": "Verification failed. Please try again.",
    }

    # Get trust score if complete
    trust_score = None
    verdict = None
    if media.status == "complete":
        ver_result = await db.execute(
            select(VerificationRecord).where(VerificationRecord.media_id == media_id)
        )
        record = ver_result.scalar_one_or_none()
        if record:
            trust_score = record.trust_score
            verdict = record.verdict

    return VerificationStatusResponse(
        media_id=media.media_id,
        status=media.status,
        progress=progress_messages.get(media.status, "Unknown status"),
        trust_score=trust_score,
        verdict=verdict,
    )


@router.get("/{media_id}/result", response_model=TrustScoreResult)
async def get_verification_result(
    media_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the full verification result with Trust Score, evidence report, and breakdown."""
    # Get verification record
    result = await db.execute(
        select(VerificationRecord).where(VerificationRecord.media_id == media_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        # Check if media exists but verification isn't complete
        media_result = await db.execute(
            select(MediaUpload).where(MediaUpload.media_id == media_id)
        )
        media = media_result.scalar_one_or_none()

        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found",
            )

        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Verification in progress (status: {media.status}). Please poll /status endpoint.",
        )

    return TrustScoreResult(
        record_id=record.record_id,
        media_id=record.media_id,
        media_type=record.media_type,
        trust_score=record.trust_score,
        verdict=record.verdict,
        recommended_action=record.recommended_action,
        model_breakdown=record.model_breakdown,
        evidence_report=record.evidence_report,
        confidence=record.confidence,
        analysis_duration_ms=record.analysis_duration_ms,
        created_at=record.created_at,
    )


@router.get("/history", response_model=VerificationHistoryResponse)
async def get_verification_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get user's verification history."""
    offset = (page - 1) * page_size

    # Count total
    count_result = await db.execute(
        select(VerificationRecord).where(VerificationRecord.user_id == user.user_id)
    )
    total = len(count_result.all())

    # Fetch records
    result = await db.execute(
        select(VerificationRecord)
        .where(VerificationRecord.user_id == user.user_id)
        .order_by(desc(VerificationRecord.created_at))
        .offset(offset)
        .limit(page_size)
    )
    records = result.scalars().all()

    return VerificationHistoryResponse(
        records=[
            TrustScoreResult(
                record_id=r.record_id,
                media_id=r.media_id,
                media_type=r.media_type,
                trust_score=r.trust_score,
                verdict=r.verdict,
                recommended_action=r.recommended_action,
                model_breakdown=r.model_breakdown,
                evidence_report=r.evidence_report,
                confidence=r.confidence,
                analysis_duration_ms=r.analysis_duration_ms,
                created_at=r.created_at,
            )
            for r in records
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
