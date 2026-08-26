"""
SatyaKavach - Verification Orchestrator
Runs the full pipeline: Preprocessing → AI Analysis → Risk Engine → Evidence Report
"""

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.media_upload import MediaUpload
from app.models.verification_record import VerificationRecord
from app.models.audit_log import AuditLog
from app.services.preprocessing.pipeline import PreprocessingPipeline
from app.services.ai.image_detector import ImageDeepfakeDetector
from app.services.ai.video_detector import VideoDeepfakeDetector
from app.services.ai.audio_detector import AudioDeepfakeDetector
from app.services.threat_intel.service import ThreatIntelligenceService
from app.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


class VerificationService:
    """Orchestrates the full media verification pipeline."""

    def __init__(self):
        self.preprocessor = PreprocessingPipeline()
        self.image_detector = ImageDeepfakeDetector()
        self.video_detector = VideoDeepfakeDetector()
        self.audio_detector = AudioDeepfakeDetector()
        self.threat_intel = ThreatIntelligenceService()
        self.risk_engine = RiskEngine()

    async def verify(self, media: MediaUpload, file_data: bytes, db: AsyncSession) -> VerificationRecord:
        """
        Full verification pipeline:
        1. Update status → preprocessing
        2. Preprocess media
        3. Run AI analysis (parallel where possible)
        4. Compute Trust Score via Risk Engine
        5. Generate evidence report
        6. Persist results
        """
        start_time = time.time()

        try:
            # ── Step 1: Preprocessing ──
            await self._update_status(media, "preprocessing", db)
            artifacts = await self.preprocessor.process(
                file_data, media.media_type, media.original_filename or "unknown", media.media_id
            )

            # ── Step 2: AI Analysis ──
            await self._update_status(media, "analyzing", db)
            image_verdict = None
            video_verdict = None
            audio_verdict = None
            threat_verdict = None

            # Image analysis
            if media.media_type in ("image", "screenshot"):
                try:
                    image_verdict = await self.image_detector.analyze(
                        file_data, media.original_filename or "image", media.media_id
                    )
                except Exception as e:
                    logger.error(f"Image detection failed: {e}")

            # Video analysis
            if media.media_type == "video":
                try:
                    video_verdict = await self.video_detector.analyze(
                        file_data, media.original_filename or "video", media.media_id
                    )
                except Exception as e:
                    logger.error(f"Video detection failed: {e}")

            # Audio analysis (for audio files or video audio tracks)
            if media.media_type == "audio":
                try:
                    audio_verdict = await self.audio_detector.analyze(
                        file_data, media.original_filename or "audio", media.media_id
                    )
                except Exception as e:
                    logger.error(f"Audio detection failed: {e}")

            # Threat intelligence (for links)
            if media.media_type == "link" and media.source_url:
                try:
                    threat_verdict = await self.threat_intel.analyze(media.source_url)
                except Exception as e:
                    logger.error(f"Threat intelligence failed: {e}")

            # ── Step 3: Risk Engine ──
            await self._update_status(media, "scoring", db)
            trust_result = self.risk_engine.compute_trust_score(
                media_type=media.media_type,
                image_verdict=image_verdict,
                video_verdict=video_verdict,
                audio_verdict=audio_verdict,
                threat_verdict=threat_verdict,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # ── Step 4: Persist Results ──
            record = VerificationRecord(
                media_id=media.media_id,
                user_id=media.user_id,
                media_type=media.media_type,
                trust_score=trust_result.trust_score,
                verdict=trust_result.verdict,
                recommended_action=trust_result.recommended_action,
                model_breakdown=trust_result.model_breakdown,
                evidence_report=trust_result.evidence_report,
                confidence=trust_result.confidence,
                analysis_duration_ms=duration_ms,
            )
            db.add(record)

            # Update media status
            media.status = "complete"
            db.add(media)

            # Audit log
            audit = AuditLog(
                user_id=media.user_id,
                media_id=media.media_id,
                event_type="analysis_complete",
                action=f"Verification completed: {trust_result.verdict} ({trust_result.trust_score}/100)",
                event_metadata={
                    "duration_ms": duration_ms,
                    "verdict": trust_result.verdict,
                    "trust_score": trust_result.trust_score,
                    "signals_used": trust_result.model_breakdown.get("available_signals", []),
                },
            )
            db.add(audit)

            await db.commit()
            await db.refresh(record)

            logger.info(
                f"Verification complete: {media.media_id} → "
                f"{trust_result.verdict} ({trust_result.trust_score}/100) "
                f"in {duration_ms}ms"
            )

            return record

        except Exception as e:
            logger.error(f"Verification failed for {media.media_id}: {e}")
            media.status = "failed"
            media.error_message = str(e)
            await db.commit()
            raise

    async def _update_status(self, media: MediaUpload, status: str, db: AsyncSession):
        """Update media status and log it."""
        media.status = status
        await db.commit()
        logger.debug(f"Media {media.media_id} status → {status}")
