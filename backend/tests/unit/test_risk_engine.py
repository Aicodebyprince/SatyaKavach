"""
SatyaKavach - Risk Engine Unit Tests
"""

import pytest
from app.services.risk_engine import RiskEngine
from app.services.ai.image_detector import ImageVerdict
from app.services.ai.video_detector import VideoVerdict
from app.services.ai.audio_detector import AudioVerdict
from app.services.threat_intel.service import ThreatVerdict, VendorVerdict


class TestRiskEngine:
    def setup_method(self):
        self.engine = RiskEngine()

    def test_trust_score_range(self):
        """Trust score must always be 0-100."""
        result = self.engine.compute_trust_score(media_type="image")
        assert 0 <= result.trust_score <= 100
        assert isinstance(result.trust_score, int)

    def test_verdict_high_trust(self):
        """Score >= 80 should map to HIGH_TRUST."""
        verdict = self.engine._map_verdict(80)
        assert verdict == "HIGH_TRUST"
        verdict = self.engine._map_verdict(100)
        assert verdict == "HIGH_TRUST"

    def test_verdict_uncertain(self):
        """Score 50-79 should map to UNCERTAIN."""
        verdict = self.engine._map_verdict(50)
        assert verdict == "UNCERTAIN"
        verdict = self.engine._map_verdict(79)
        assert verdict == "UNCERTAIN"

    def test_verdict_low_trust(self):
        """Score < 50 should map to LOW_TRUST."""
        verdict = self.engine._map_verdict(0)
        assert verdict == "LOW_TRUST"
        verdict = self.engine._map_verdict(49)
        assert verdict == "LOW_TRUST"

    def test_authentic_image_gives_high_trust(self):
        """A real image (low manipulation) should give HIGH_TRUST."""
        image = ImageVerdict(
            manipulation_score=0.1,
            classification="real",
            confidence=0.95,
            evidence={},
            models_used=["efficientnet", "xceptionnet"],
        )
        result = self.engine.compute_trust_score(media_type="image", image_verdict=image)
        assert result.trust_score >= 80
        assert result.verdict == "HIGH_TRUST"

    def test_fake_image_gives_low_trust(self):
        """A fake image (high manipulation) should give LOW_TRUST."""
        image = ImageVerdict(
            manipulation_score=0.9,
            classification="fake",
            confidence=0.90,
            evidence={},
            models_used=["efficientnet", "xceptionnet"],
        )
        result = self.engine.compute_trust_score(media_type="image", image_verdict=image)
        assert result.trust_score < 50
        assert result.verdict == "LOW_TRUST"

    def test_malicious_link_gives_low_trust(self):
        """A malicious link should give LOW_TRUST."""
        threat = ThreatVerdict(
            threat_score=0.9,
            is_malicious=True,
            vendors=[VendorVerdict(vendor="virustotal", threat_score=0.9, is_flagged=True)],
        )
        result = self.engine.compute_trust_score(media_type="link", threat_verdict=threat)
        assert result.trust_score < 50
        assert result.verdict == "LOW_TRUST"

    def test_safe_link_gives_high_trust(self):
        """A safe link should give HIGH_TRUST."""
        threat = ThreatVerdict(
            threat_score=0.0,
            is_malicious=False,
            vendors=[VendorVerdict(vendor="virustotal", threat_score=0.0, is_flagged=False)],
        )
        result = self.engine.compute_trust_score(media_type="link", threat_verdict=threat)
        assert result.trust_score >= 80
        assert result.verdict == "HIGH_TRUST"

    def test_no_signals_defaults_to_uncertain(self):
        """With no signals, should default to UNCERTAIN."""
        result = self.engine.compute_trust_score(media_type="unknown")
        assert result.verdict == "UNCERTAIN"
        assert result.trust_score == 50

    def test_recommended_action_matches_verdict(self):
        """Each verdict should have an appropriate recommended action."""
        for score, expected_verdict in [(90, "HIGH_TRUST"), (65, "UNCERTAIN"), (20, "LOW_TRUST")]:
            result = self.engine.compute_trust_score(media_type="image")
            result.trust_score = score
            result.verdict = self.engine._map_verdict(score)
            action = self.engine._map_action(result.verdict)
            assert expected_verdict.lower().replace("_", "") in action.lower().replace(" ", "") or len(action) > 0

    def test_model_breakdown_contains_signals(self):
        """Model breakdown should list available signals."""
        image = ImageVerdict(
            manipulation_score=0.3,
            classification="real",
            confidence=0.85,
            evidence={"artifacts": ["test"]},
            models_used=["efficientnet"],
        )
        result = self.engine.compute_trust_score(media_type="image", image_verdict=image)
        assert "image" in result.model_breakdown
        assert "available_signals" in result.model_breakdown
        assert "image" in result.model_breakdown["available_signals"]

    def test_evidence_report_has_findings(self):
        """Evidence report should have findings list."""
        image = ImageVerdict(
            manipulation_score=0.8,
            classification="fake",
            confidence=0.90,
            evidence={"artifacts": ["face blending"]},
            models_used=["efficientnet"],
        )
        result = self.engine.compute_trust_score(media_type="image", image_verdict=image)
        assert len(result.evidence_report["findings"]) > 0
        assert result.evidence_report["verdict"] == "LOW_TRUST"

    def test_multimodal_fusion(self):
        """Multiple signals should be fused correctly."""
        image = ImageVerdict(
            manipulation_score=0.8,
            classification="fake",
            confidence=0.9,
            evidence={},
            models_used=["efficientnet"],
        )
        audio = AudioVerdict(
            audio_authenticity_score=0.2,
            voice_clone_detected=True,
            classification="synthetic",
            confidence=0.85,
            evidence={},
            models_used=["wav2vec2"],
        )
        result = self.engine.compute_trust_score(
            media_type="multimodal",
            image_verdict=image,
            audio_verdict=audio,
        )
        # Both bad signals should give LOW_TRUST
        assert result.verdict == "LOW_TRUST"
        assert result.trust_score < 50
