"""
SatyaKavach - AI Detector Unit Tests
"""

import pytest
import asyncio
from app.services.ai.image_detector import ImageDeepfakeDetector, ImageVerdict
from app.services.ai.video_detector import VideoDeepfakeDetector, VideoVerdict
from app.services.ai.audio_detector import AudioDeepfakeDetector, AudioVerdict


class TestImageDetector:
    def setup_method(self):
        self.detector = ImageDeepfakeDetector()

    @pytest.mark.asyncio
    async def test_returns_image_verdict(self):
        """Detector should return an ImageVerdict."""
        result = await self.detector.analyze(b"test-data", "test.jpg", "test-123")
        assert isinstance(result, ImageVerdict)
        assert 0.0 <= result.manipulation_score <= 1.0
        assert result.classification in ("fake", "real")
        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_has_models_used(self):
        """Verdict should list models used."""
        result = await self.detector.analyze(b"test", "photo.png", "id-1")
        assert len(result.models_used) > 0

    @pytest.mark.asyncio
    async def test_has_evidence(self):
        """Verdict should have evidence."""
        result = await self.detector.analyze(b"test", "face.jpg", "id-2")
        assert "efficientnet_score" in result.evidence
        assert "fusion_score" in result.evidence


class TestVideoDetector:
    def setup_method(self):
        self.detector = VideoDeepfakeDetector()

    @pytest.mark.asyncio
    async def test_returns_video_verdict(self):
        result = await self.detector.analyze(b"test-video", "clip.mp4", "vid-123")
        assert isinstance(result, VideoVerdict)
        assert 0.0 <= result.video_authenticity_score <= 1.0
        assert result.classification in ("authentic", "manipulated")

    @pytest.mark.asyncio
    async def test_has_frame_detections(self):
        result = await self.detector.analyze(b"test", "video.mp4", "vid-2")
        assert len(result.frame_detections) > 0


class TestAudioDetector:
    def setup_method(self):
        self.detector = AudioDeepfakeDetector()

    @pytest.mark.asyncio
    async def test_returns_audio_verdict(self):
        result = await self.detector.analyze(b"test-audio", "voice.wav", "aud-123")
        assert isinstance(result, AudioVerdict)
        assert 0.0 <= result.audio_authenticity_score <= 1.0
        assert result.classification in ("authentic", "synthetic")

    @pytest.mark.asyncio
    async def test_has_transcript(self):
        result = await self.detector.analyze(b"test", "speech.mp3", "aud-2")
        assert result.transcript is not None

    @pytest.mark.asyncio
    async def test_voice_clone_detection(self):
        result = await self.detector.analyze(b"test", "clone.wav", "aud-3")
        assert isinstance(result.voice_clone_detected, bool)
