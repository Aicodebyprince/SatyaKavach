"""
SatyaKavach - Upload & Intake API
Handles media upload, validation, storage, and verification job creation
"""

import logging
from typing import Optional

try:
    import magic  # libmagic-based MIME sniffing (not available on plain Windows)
except ImportError:  # pragma: no cover
    magic = None

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.storage import storage
from app.models.user import User
from app.models.media_upload import MediaUpload
from app.models.verification_record import VerificationRecord
from app.api.v1.deps import get_current_user
from app.schemas.media import MediaUploadResponse, LinkSubmitRequest
from app.services.verification import VerificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])
verification_service = VerificationService()


@router.post("/", response_model=MediaUploadResponse)
async def upload_media(
    file: Optional[UploadFile] = File(None),
    media_type: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload media for verification.
    Accepts images (PNG/JPEG/WebP), videos (MP4/MOV/AVI), audio (MP3/WAV/M4A).
    Returns media_id and starts async verification.
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided. Please upload a file or use /link endpoint.",
        )

    # Read file data
    file_data = await file.read()
    file_size = len(file_data)

    # Validate file size
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded",
        )

    # Detect MIME type (browser-provided first, magic-byte sniff as fallback)
    mime_type = file.content_type
    if not mime_type:
        if magic is not None:
            mime_type = magic.from_buffer(file_data[:2048], mime=True)
        else:
            import mimetypes
            mime_type = (
                mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
            )

    # Auto-detect media type if not provided
    if not media_type:
        if mime_type.startswith("image/"):
            media_type = "image"
        elif mime_type.startswith("video/"):
            media_type = "video"
        elif mime_type.startswith("audio/"):
            media_type = "audio"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {mime_type}",
            )

    # Validate MIME type
    allowed_types = (
        settings.ALLOWED_IMAGE_TYPES +
        settings.ALLOWED_VIDEO_TYPES +
        settings.ALLOWED_AUDIO_TYPES
    )
    if mime_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{mime_type}' not supported. Allowed: {', '.join(allowed_types)}",
        )

    # Compute SHA-256 for deduplication
    sha256 = storage.compute_sha256(file_data)

    # Check for duplicate
    existing = await db.execute(
        select(MediaUpload).where(MediaUpload.sha256 == sha256)
    )
    existing_media = existing.scalar_one_or_none()

    if existing_media and existing_media.status == "complete":
        # Return existing verification result
        return MediaUploadResponse(
            media_id=existing_media.media_id,
            media_type=existing_media.media_type,
            status="complete",
            message="Media already verified. Returning cached result.",
            created_at=existing_media.created_at,
        )

    # Upload to S3
    s3_key = storage.upload_file(file_data, f"new_{sha256[:8]}", file.filename or "upload")

    # Create media record
    media = MediaUpload(
        user_id=user.user_id if user else None,
        media_type=media_type,
        channel="web",
        original_filename=file.filename,
        s3_key=s3_key,
        file_size_bytes=file_size,
        mime_type=mime_type,
        sha256=sha256,
        language=language,
        status="queued",
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    # Run verification (synchronous for demo; use Celery/Celery in production)
    try:
        record = await verification_service.verify(media, file_data, db)
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        media.status = "failed"
        media.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )

    return MediaUploadResponse(
        media_id=media.media_id,
        media_type=media.media_type,
        status="complete",
        message="Verification complete",
        created_at=media.created_at,
    )


@router.post("/link", response_model=MediaUploadResponse)
async def submit_link(
    request: LinkSubmitRequest,
    user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a URL/link for threat intelligence verification."""
    from urllib.parse import urlparse

    # Validate URL
    try:
        parsed = urlparse(request.url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("Invalid URL")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format",
        )

    # Compute hash for deduplication
    import hashlib
    sha256 = hashlib.sha256(request.url.encode()).hexdigest()

    # Create media record for link
    media = MediaUpload(
        user_id=user.user_id if user else None,
        media_type="link",
        channel="web",
        source_url=request.url,
        s3_key=f"links/{sha256[:8]}",
        file_size_bytes=0,
        mime_type="text/uri-list",
        sha256=sha256,
        language=request.language,
        status="queued",
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    # Run verification
    try:
        await verification_service.verify(media, b"", db)
    except Exception as e:
        logger.error(f"Link verification failed: {e}")
        media.status = "failed"
        media.error_message = str(e)
        await db.commit()

    return MediaUploadResponse(
        media_id=media.media_id,
        media_type="link",
        status=media.status,
        message="Link verification complete" if media.status == "complete" else "Verification in progress",
        created_at=media.created_at,
    )
