"""
SatyaKavach - Celery Worker
Async job processing for media verification
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "satyakavach",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 min hard limit
    task_soft_time_limit=240,  # 4 min soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)


@celery_app.task(bind=True, max_retries=3)
def verify_media_task(self, media_id: str, file_data_b64: str):
    """
    Async verification task.
    In production, this would be called instead of synchronous verification.
    """
    import base64
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.services.verification import VerificationService
    from app.models.media_upload import MediaUpload
    from sqlalchemy import select

    async def _run():
        service = VerificationService()
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(MediaUpload).where(MediaUpload.media_id == media_id)
            )
            media = result.scalar_one_or_none()
            if not media:
                return {"error": "Media not found"}

            file_data = base64.b64decode(file_data_b64)
            record = await service.verify(media, file_data, db)
            return {
                "media_id": media_id,
                "trust_score": record.trust_score,
                "verdict": record.verdict,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
