"""
SatyaKavach - Preprocessing Pipeline
Normalizes raw media into formats consumable by AI detection models.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
from PIL import Image
import io

from app.core.config import settings

logger = logging.getLogger(__name__)

# Haar cascade for face detection (shipped with OpenCV)
_FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_face_cascade = cv2.CascadeClassifier(_FACE_CASCADE_PATH)

# Minimum face size (pixels) to avoid noise
_MIN_FACE_SIZE = (30, 30)


@dataclass
class FaceTile:
    """A detected and cropped face region."""
    face_index: int
    crop_bytes: bytes  # JPEG bytes of the cropped face
    bbox: tuple[int, int, int, int]  # (x, y, w, h) in original image coords
    confidence: float = 1.0


@dataclass
class PreprocessedArtifacts:
    """Artifacts extracted during preprocessing."""
    media_type: str
    face_tiles: list[bytes] = field(default_factory=list)
    face_details: list[FaceTile] = field(default_factory=list)
    keyframes: list[bytes] = field(default_factory=list)
    audio_track: Optional[bytes] = None
    spectrogram: Optional[bytes] = None
    extracted_text: Optional[str] = None
    ocr_boxes: list[dict] = field(default_factory=list)


class PreprocessingPipeline:
    """
    Preprocess uploaded media based on type:
    - Image: face detection via OpenCV Haar cascade, cropping & alignment
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
            artifacts.face_tiles = [file_data]
            return artifacts

        try:
            # Decode image with OpenCV
            nparr = np.frombuffer(file_data, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if cv_img is None:
                logger.warning(f"Could not decode image {filename}, using raw data")
                artifacts.face_tiles = [file_data]
                return artifacts

            height, width = cv_img.shape[:2]
            logger.info(f"Image loaded: {width}x{height}")

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = _face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=_MIN_FACE_SIZE,
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            if len(faces) == 0:
                # No faces found — use the full image (might be a deepfake without
                # standard face structure, or a landscape/scene image)
                logger.info(f"No faces detected in {filename}, using full image")
                artifacts.face_tiles = [file_data]
                artifacts.face_details = [FaceTile(
                    face_index=0,
                    crop_bytes=file_data,
                    bbox=(0, 0, width, height),
                    confidence=0.5,
                )]
                return artifacts

            logger.info(f"Detected {len(faces)} face(s) in {filename}")

            for i, (x, y, w, h) in enumerate(faces):
                # Expand bounding box by 20% for context
                pad_w = int(w * 0.2)
                pad_h = int(h * 0.2)
                x1 = max(0, x - pad_w)
                y1 = max(0, y - pad_h)
                x2 = min(width, x + w + pad_w)
                y2 = min(height, y + h + pad_h)

                # Crop face region
                face_crop = cv_img[y1:y2, x1:x2]

                # Encode to JPEG bytes
                _, buffer = cv2.imencode(".jpg", face_crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
                face_bytes = buffer.tobytes()

                artifacts.face_tiles.append(face_bytes)
                artifacts.face_details.append(FaceTile(
                    face_index=i,
                    crop_bytes=face_bytes,
                    bbox=(x1, y1, x2 - x1, y2 - y1),
                    confidence=1.0,
                ))

            logger.info(f"Cropped {len(artifacts.face_tiles)} face tile(s)")

        except Exception as e:
            logger.error(f"Face detection failed for {filename}: {e}")
            # Graceful fallback: use the original image
            artifacts.face_tiles = [file_data]

        return artifacts

    async def _process_video(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process video: extract keyframes and audio track."""
        artifacts = PreprocessedArtifacts(media_type="video")

        try:
            # Decode video frames with OpenCV
            nparr = np.frombuffer(file_data, np.uint8)
            cap = cv2.VideoCapture(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

            # Fallback if OpenCV can't decode the video container
            if not cap.isOpened():
                logger.warning(f"OpenCV could not open video {filename}, using raw data")
                artifacts.keyframes = [file_data]
                artifacts.audio_track = file_data
                return artifacts

            fps = cap.get(cv2.CAP_PROP_FPS) or 1.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, int(fps))  # ~1 frame per second

            frame_idx = 0
            sampled = 0
            max_keyframes = 10

            while cap.isOpened() and sampled < max_keyframes:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % sample_interval == 0:
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    artifacts.keyframes.append(buf.tobytes())
                    sampled += 1
                frame_idx += 1

            cap.release()
            logger.info(f"Extracted {len(artifacts.keyframes)} keyframes from {filename} ({total_frames} total frames)")

            # Audio track: pass through raw data (audio_detector handles its own decoding)
            artifacts.audio_track = file_data

        except Exception as e:
            logger.error(f"Video preprocessing failed for {filename}: {e}")
            # Graceful fallback
            artifacts.keyframes = [file_data]
            artifacts.audio_track = file_data

        return artifacts

    async def _process_audio(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process audio: pass through raw data and generate spectrogram."""
        artifacts = PreprocessedArtifacts(media_type="audio")

        try:
            artifacts.audio_track = file_data

            # Generate mel-spectrogram using numpy (no librosa dependency)
            # Simple FFT-based spectrogram as a fallback
            audio_np = np.frombuffer(file_data[:len(file_data) - (len(file_data) % 2)], dtype=np.int16)
            if len(audio_np) > 0:
                # Take FFT and build a simple spectrogram representation
                fft = np.abs(np.fft.rfft(audio_np.astype(np.float32)))
                # Downsample to a compact representation
                chunk_size = max(1, len(fft) // 128)
                spectrogram = fft[:chunk_size * 128].reshape(chunk_size, 128).mean(axis=0)
                artifacts.spectrogram = spectrogram.tobytes()
            else:
                artifacts.spectrogram = file_data[:500]

            logger.info(f"Audio preprocessed: {filename} ({len(file_data)} bytes)")

        except Exception as e:
            logger.error(f"Audio preprocessing failed for {filename}: {e}")
            artifacts.audio_track = file_data
            artifacts.spectrogram = file_data[:500]

        return artifacts

    async def _process_screenshot(self, file_data: bytes, filename: str, media_id: str) -> PreprocessedArtifacts:
        """Process screenshot: extract text via OCR (graceful fallback if unavailable)."""
        artifacts = PreprocessedArtifacts(media_type="screenshot")

        try:
            # Try EasyOCR if available
            import easyocr
            reader = easyocr.Reader(["hi", "en"], verbose=False)
            results = reader.readtext(file_data)

            texts = []
            for (bbox, text, conf) in results:
                texts.append(text)
                artifacts.ocr_boxes.append({
                    "text": text,
                    "bbox": [[int(c) for c in pt] for pt in bbox],
                    "confidence": round(conf, 3),
                })
            artifacts.extracted_text = " ".join(texts) if texts else None
            logger.info(f"OCR extracted {len(texts)} text blocks from {filename}")

        except ImportError:
            logger.info("EasyOCR not installed, skipping OCR extraction")
            artifacts.extracted_text = None
        except Exception as e:
            logger.error(f"OCR extraction failed for {filename}: {e}")

        # Always process the image for face detection too
        if not artifacts.face_tiles:
            artifacts.face_tiles = [file_data]

        return artifacts
