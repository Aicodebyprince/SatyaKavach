"""
SatyaKavach - Image Pipeline Integration Tests
Tests the full pipeline: preprocessing → face detection → ONNX inference → risk engine
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path

# Force real models for integration tests
os.environ["DEMO_MODE"] = "false"

from app.services.ai.image_detector import ImageDeepfakeDetector, ImageVerdict
from app.services.preprocessing.pipeline import PreprocessingPipeline
from app.services.risk_engine import RiskEngine

# Path to training dataset images (go up to project root)
DATASET_DIR = Path(__file__).resolve().parent.parent.parent.parent / "training" / "datasets" / "combined"


def _find_test_image():
    """Find an actual image file from the training dataset."""
    fake_dir = DATASET_DIR / "fake"
    if fake_dir.exists():
        for f in sorted(fake_dir.iterdir()):
            if f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                return f
    return None


TEST_IMAGE = _find_test_image()


class TestPreprocessingPipeline:
    """Test the preprocessing pipeline with real images."""

    def setup_method(self):
        self.pipeline = PreprocessingPipeline()

    @pytest.mark.asyncio
    async def test_face_detection_on_real_image(self):
        """Preprocessing should detect at least one face tile from a real image."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()
        artifacts = await self.pipeline.process(file_data, "image", TEST_IMAGE.name, "test-001")

        assert artifacts.media_type == "image"
        assert len(artifacts.face_tiles) >= 1, "Should detect at least one face tile"
        assert len(artifacts.face_details) >= 1, "Should have face details"
        assert artifacts.face_details[0].face_index == 0
        assert len(artifacts.face_details[0].crop_bytes) > 0

    @pytest.mark.asyncio
    async def test_face_detection_returns_valid_jpeg(self):
        """Each face tile should be valid JPEG bytes."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()
        artifacts = await self.pipeline.process(file_data, "image", TEST_IMAGE.name, "test-002")

        from PIL import Image
        import io

        for tile in artifacts.face_tiles:
            img = Image.open(io.BytesIO(tile))
            assert img.format == "JPEG"
            assert img.size[0] > 0 and img.size[1] > 0


class TestImageDetectorIntegration:
    """Test the image detector with real ONNX models."""

    def setup_method(self):
        self.detector = ImageDeepfakeDetector()
        self.risk_engine = RiskEngine()

    @pytest.mark.asyncio
    async def test_real_inference_on_fake_image(self):
        """ONNX models should produce a manipulation score on a real image."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()
        verdict = await self.detector.analyze(file_data, TEST_IMAGE.name, "test-001")

        assert isinstance(verdict, ImageVerdict)
        assert 0.0 <= verdict.manipulation_score <= 1.0
        assert verdict.classification in ("fake", "real")
        assert 0.0 <= verdict.confidence <= 1.0
        assert len(verdict.models_used) >= 1
        assert "fusion_score" in verdict.evidence

    @pytest.mark.asyncio
    async def test_face_tiles_from_preprocessing(self):
        """Detector should work with pre-cropped face tiles."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()
        pipeline = PreprocessingPipeline()
        artifacts = await pipeline.process(file_data, "image", TEST_IMAGE.name, "test-002")

        verdict = await self.detector.analyze(
            file_data, TEST_IMAGE.name, "test-002",
            face_tiles=artifacts.face_tiles,
        )

        assert isinstance(verdict, ImageVerdict)
        assert len(verdict.per_face_scores) >= 1
        assert verdict.per_face_scores[0]["face_index"] == 0

    @pytest.mark.asyncio
    async def test_risk_engine_with_real_verdict(self):
        """Risk Engine should produce a Trust Score from real model output."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()
        verdict = await self.detector.analyze(file_data, TEST_IMAGE.name, "test-003")

        result = self.risk_engine.compute_trust_score(
            media_type="image",
            image_verdict=verdict,
        )

        assert 0 <= result.trust_score <= 100
        assert result.verdict in ("HIGH_TRUST", "UNCERTAIN", "LOW_TRUST")
        assert len(result.recommended_action) > 0
        assert "image" in result.model_breakdown
        assert "findings" in result.evidence_report
        assert "signals available" in result.evidence_report["analysis_completeness"]

    @pytest.mark.asyncio
    async def test_full_pipeline_with_face_tiles(self):
        """Full pipeline: preprocess → detect → risk engine → evidence report."""
        if TEST_IMAGE is None:
            pytest.skip("No test image found in training dataset")

        file_data = TEST_IMAGE.read_bytes()

        # Step 1: Preprocess
        pipeline = PreprocessingPipeline()
        artifacts = await pipeline.process(file_data, "image", TEST_IMAGE.name, "test-full")

        # Step 2: Detect
        verdict = await self.detector.analyze(
            file_data, TEST_IMAGE.name, "test-full",
            face_tiles=artifacts.face_tiles,
        )

        # Step 3: Risk Engine
        result = self.risk_engine.compute_trust_score(
            media_type="image",
            image_verdict=verdict,
        )

        # Verify the complete pipeline
        assert result.trust_score >= 0
        assert result.evidence_report["trust_score"] == result.trust_score
        assert len(result.evidence_report["findings"]) >= 1
        assert len(result.evidence_report["artifacts"]) >= 1
        print(f"\n  [Pipeline] Trust Score: {result.trust_score}/100 -> {result.verdict}")
        print(f"  [Pipeline] Faces detected: {verdict.evidence.get('total_faces_detected', 'N/A')}")
        print(f"  [Pipeline] Models: {verdict.models_used}")
        print(f"  [Pipeline] Finding: {result.evidence_report['findings'][0]['message']}")
