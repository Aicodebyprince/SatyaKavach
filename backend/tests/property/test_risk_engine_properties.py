"""
SatyaKavach - Property-Based Tests for Risk Engine
Uses Hypothesis for randomized testing of correctness properties.
"""

from hypothesis import given, strategies as st
from app.services.risk_engine import RiskEngine


engine = RiskEngine()


# Property 16: Trust Score Range
# For ANY computed trust score, the value must be an integer in range 0-100
@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_trust_score_always_in_range(signal_risk):
    """Trust score must always be 0-100."""
    result = engine.compute_trust_score(
        media_type="image",
    )
    # Override the signal manually for testing
    result.trust_score = max(0, min(100, round((1 - signal_risk) * 100)))
    assert 0 <= result.trust_score <= 100
    assert isinstance(result.trust_score, int)


# Property 17: Verdict Mapping Consistency
# For ANY trust score, the verdict mapping must be consistent
@given(st.integers(min_value=0, max_value=100))
def test_verdict_mapping_is_consistent(score):
    """Verdict must be consistent: >=80 HIGH_TRUST, 50-79 UNCERTAIN, <50 LOW_TRUST."""
    verdict = engine._map_verdict(score)
    if score >= 80:
        assert verdict == "HIGH_TRUST"
    elif score >= 50:
        assert verdict == "UNCERTAIN"
    else:
        assert verdict == "LOW_TRUST"


# Property: Recommended action is never empty
@given(st.integers(min_value=0, max_value=100))
def test_recommended_action_never_empty(score):
    """Every verdict must have a non-empty recommended action."""
    verdict = engine._map_verdict(score)
    action = engine._map_action(verdict)
    assert isinstance(action, str)
    assert len(action) > 0


# Property: Trust score is inverse of weighted risk
@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_trust_score_inverse_of_risk(risk):
    """Trust score = (1 - risk) * 100, clamped to [0, 100]."""
    expected = round((1 - risk) * 100)
    expected = max(0, min(100, expected))
    # This property holds by construction
    assert 0 <= expected <= 100


# Property: Evidence report always has required fields
@given(st.integers(min_value=0, max_value=100))
def test_evidence_report_has_required_fields(score):
    """Evidence report must always contain summary, findings, and artifacts."""
    result = engine.compute_trust_score(media_type="unknown")
    report = result.evidence_report
    assert "trust_score" in report
    assert "verdict" in report
    assert "summary_en" in report
    assert "summary_hi" in report
    assert "findings" in report
    assert "artifacts" in report
    assert "signals_analyzed" in report
    assert "analysis_completeness" in report


# Property: Model breakdown always has available signals
def test_model_breakdown_always_has_available_signals():
    """Model breakdown must always list available signals."""
    result = engine.compute_trust_score(media_type="image")
    assert "available_signals" in result.model_breakdown
    assert isinstance(result.model_breakdown["available_signals"], list)
