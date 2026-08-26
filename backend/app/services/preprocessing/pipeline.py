"""
SatyaKavach - Preprocessing Pipeline
Normalizes raw media into formats consumable by AI detection models.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PreprocessedArtifacts:
    """Artifacts extracted during preprocessing."""
    media_type: str
    face_tiles: list[bytes] = None
    keyframes: list[bytes] = None
    audio_track: Optional[bytes] = None
    spectrogram: Optional[bytes] = None
    extracted_text: Optional[str] = None
    ocr_boxes: list[dict] = None

    def __post_init__(self):
        if self.face_tiles is None:
            self.face_tiles = []
        if self.keyframes is None:
            self.keyframes = []
        if self.ocr_boxes is None:
            self.ocr_boxes = []


class PreprocessingPipeline:
    """
    Preprocess uploaded media based on type:
    - Image: face detection, cropping, alignment
    - Video: keyframe extraction, face tracking, audio track extraction
    - Audio: WAV conversion, spectrogram generation
    - Screenshot: OCR text extraction
    """

    async def process(self, file_data: bytes, media_type: str, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Route to the appropriate preprocessing pipeline."""
        logger.info(f"Preprocessing {media_type}: {filename} ({media_id})")

        if media_type == "image":
            return await self._process_image(file_data, filename, media_id)
        elif media_type == "video":
            return await self._process_video(file_data, filename, media_id)
        elif media_type == "audio":
            return await self._process_audio(file_data, filename, media_id)
        elif media_type == "screenshot":
            return await self._process_screenshot(file_data, filename, media_id)
        elif media_type == "link":
            return PreprocessedArtifacts(media_type="link")
        else:
            return PreprocessedArtifacts(media_type=media_type)

    async def _process_image(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process image: detect and crop faces for deepfake analysis."""
        artifacts = PreprocessedArtifacts(media_type="image")

        if settings.DEMO_MODE:
            # In demo mode, simulate face detection
            artifacts.face_tiles = [file_data]  # Pretend we found one face
            return artifacts

        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(file_data))
            logger.info(f"Image loaded: {img.size} {img.mode}")

            # In production: use face detection model (e.g., MTCNN, RetinaFace)
            # For now, use the full image as a "face tile"
            artifacts.face_tiles = [file_data]
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            artifacts.face_tiles = [file_data]

        return artifacts

    async def _process_video(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process video: extract keyframes and audio track."""
        artifacts = PreprocessedArtifacts(media_type="video")

        if settings.DEMO_MODE:
            # Simulate keyframe extraction
            artifacts.keyframes = [file_data[:1000]] * 5  # 5 mock keyframes
            artifacts.audio_track = file_data[:1000]
            return artifacts

        try:
            # In production: use ffmpeg for frame extraction
            # import subprocess
            # subprocess.run(["ffmpeg", "-i", input_path, "-vf", "fps=1", frame_pattern])
            logger.info("Video keyframe extraction (demo mode)")
            artifacts.keyframes = [file_data[:1000]] * 5
            artifacts.audio_track = file_data[:1000]
        except Exception as e:
            logger.error(f"Video preprocessing failed: {e}")

        return artifacts

    async def _process_audio(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process audio: convert to WAV and generate spectrogram."""
        artifacts = PreprocessedArtifacts(media_type="audio")

        if settings.DEMO_MODE:
            artifacts.audio_track = file_data
            artifacts.spectrogram = file_data[:500]
            return artifacts

        try:
            artifacts.audio_track = file_data
            # In production: generate mel-spectrogram using librosa
            # import librosa
            # y, sr = librosa.load(io.BytesIO(file_data))
            # S = librosa.feature.melspectrogram(y=y, sr=sr)
            artifacts.spectrogram = file_data[:500]
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")

        return artifacts

    async def _process_screenshot(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process screenshot: extract text via EasyOCR."""
        artifacts = PreprocessedArtifacts(media_type="screenshot")

        if settings.DEMO_MODE:
            artifacts.extracted_text = "Demo OCR text extracted from screenshot"
            artifacts.ocr_boxes = [{"text": "Demo text", "bbox": [0, 0, 100, 20], "confidence": 0.95}]
            return artifacts

        try:
            # In production: use EasyOCR
            # import easyocr
            # reader = easyocr.Reader(['hi', 'en'])
            # results = reader.readtext(file_data)
            logger.info("OCR text extraction (demo mode)")
            artifacts.extracted_text = "Demo OCR text"
            artifacts.ocr_boxes = [{"text": "Demo", "bbox": [0, 0, 50, 20], "confidence": 0.9}]
        except Exception as e:
            logger.error(f"OCR preprocessing failed: {e}")

        return artifacts
