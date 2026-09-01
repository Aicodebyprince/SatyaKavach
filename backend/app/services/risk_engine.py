"""
SatyaKavach - Risk Engine (Multimodal Reasoning)
Fuses all available signals into a Unified Trust Score (0-100) and verdict.
This is the CORE intelligence layer of the platform.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Any

from app.core.config import settings
from app.services.ai.image_detector import ImageVerdict
from app.services.ai.video_detector import VideoVerdict
from app.services.ai.audio_detector import AudioVerdict
from app.services.threat_intel.service import ThreatVerdict
from app.services.forensics.metadata_analyzer import MetadataVerdict
from app.services.forensics.screenshot_analyzer import ScreenshotVerdict

logger = logging.getLogger(__name__)


@dataclass
class TrustResult:
    trust_score: int  # 0-100
    verdict: str  # HIGH_TRUST, UNCERTAIN, LOW_TRUST
    recommended_action: str
    model_breakdown: dict[str, Any]
    evidence_report: dict[str, Any]
    confidence: float
    analysis_duration_ms: int


class RiskEngine:
    """
    Multimodal Risk Engine — fuses image, video, audio, OCR/NLP, and threat
    intelligence signals into a single Unified Trust Score.
    
    Trust Score = (1 - weighted_risk) * 100
    
    Verdict Mapping:
        >= 80 → HIGH_TRUST
        50-79 → UNCERTAIN
        < 50  → LOW_TRUST
    """

    WEIGHTS = {
        "image": settings.RISK_WEIGHT_IMAGE,
        "video": settings.RISK_WEIGHT_VIDEO,
        "audio": settings.RISK_WEIGHT_AUDIO,
        "ocr_nlp": settings.RISK_WEIGHT_OCR_NLP,
        "threat": settings.RISK_WEIGHT_THREAT,
        "metadata": 0.10,
        "screenshot": 0.10,
    }

    def compute_trust_score(
        self,
        media_type: str,
        image_verdict: Optional[ImageVerdict] = None,
        video_verdict: Optional[VideoVerdict] = None,
        audio_verdict: Optional[AudioVerdict] = None,
        threat_verdict: Optional[ThreatVerdict] = None,
        ocr_nlp_score: Optional[float] = None,
        metadata_verdict: Optional[MetadataVerdict] = None,
        screenshot_verdict: Optional[ScreenshotVerdict] = None,
    ) -> TrustResult:
        """
        Compute the Unified Trust Score from all available signals.
        
        Each signal is normalized to a 0-1 risk value:
          0.0 = fully trustworthy, 1.0 = fully manipulated/malicious
        
        The weighted average risk is then converted to Trust Score:
          trust_score = (1 - weighted_risk) * 100
        """
        start_time = time.time()

        # ── Normalize available signals to risk values (0 = safe, 1 = risk) ──
        signals: dict[str, float] = {}

        if image_verdict is not None:
            # Image: manipulation_score is already 0-1 (higher = more fake)
            signals["image"] = image_verdict.manipulation_score

        if video_verdict is not None:
            # Video: invert authenticity_score (higher authenticity = lower risk)
            signals["video"] = 1.0 - video_verdict.video_authenticity_score

        if audio_verdict is not None:
            # Audio: invert authenticity_score
            signals["audio"] = 1.0 - audio_verdict.audio_authenticity_score

        if threat_verdict is not None:
            # Threat: threat_score is already 0-1 (higher = more malicious)
            signals["threat"] = threat_verdict.threat_score

        if ocr_nlp_score is not None:
            signals["ocr_nlp"] = ocr_nlp_score

        if metadata_verdict is not None:
            # Metadata: risk_score is already 0-1 (higher = more suspicious)
            signals["metadata"] = metadata_verdict.risk_score

        if screenshot_verdict is not None:
            # Screenshot: risk_score is already 0-1 (higher = more suspicious)
            signals["screenshot"] = screenshot_verdict.risk_score

        # ── Compute weighted risk (re-normalize over available signals) ──
        if not signals:
            # No signals available
            trust_score = 50  # Default to UNCERTAIN
            weighted_risk = 0.5
            confidence = 0.0
        else:
            total_weight = sum(self.WEIGHTS[k] for k in signals)
            weighted_risk = sum(
                self.WEIGHTS[k] * signals[k] for k in signals
            ) / total_weight
            trust_score = round((1.0 - weighted_risk) * 100)
            trust_score = max(0, min(100, trust_score))

            # Confidence based on how many signals are available
            signal_coverage = len(signals) / len(self.WEIGHTS)
            avg_confidence = self._compute_avg_confidence(
                image_verdict, video_verdict, audio_verdict
            )
            confidence = round(signal_coverage * avg_confidence, 3)

        # ── Map to verdict ──
        verdict = self._map_verdict(trust_score)
        recommended_action = self._map_action(verdict)

        # ── Build model breakdown ──
        model_breakdown = self._build_model_breakdown(
            image_verdict, video_verdict, audio_verdict, threat_verdict,
            metadata_verdict, screenshot_verdict, signals
        )

        # ── Build evidence report ──
        evidence_report = self._build_evidence_report(
            trust_score, verdict, signals, image_verdict,
            video_verdict, audio_verdict, threat_verdict,
            metadata_verdict, screenshot_verdict
        )

        duration_ms = int((time.time() - start_time) * 1000)

        return TrustResult(
            trust_score=trust_score,
            verdict=verdict,
            recommended_action=recommended_action,
            model_breakdown=model_breakdown,
            evidence_report=evidence_report,
            confidence=confidence,
            analysis_duration_ms=duration_ms,
        )

    def _map_verdict(self, score: int) -> str:
        """Map trust score to verdict."""
        if score >= settings.TRUST_HIGH_THRESHOLD:
            return "HIGH_TRUST"
        elif score >= settings.TRUST_UNCERTAIN_THRESHOLD:
            return "UNCERTAIN"
        else:
            return "LOW_TRUST"

    def _map_action(self, verdict: str) -> str:
        """Map verdict to recommended action."""
        actions = {
            "HIGH_TRUST": "This media is likely authentic. Verify context before sharing.",
            "UNCERTAIN": "Further verification recommended. Cross-check the source and look for additional evidence.",
            "LOW_TRUST": "High risk of manipulation detected. Do not share this media. Report to I4C/1930 if applicable.",
        }
        return actions[verdict]

    def _compute_avg_confidence(self, image, video, audio) -> float:
        """Average confidence across available detectors."""
        confidences = []
        if image and hasattr(image, "confidence"):
            confidences.append(image.confidence)
        if video and hasattr(video, "confidence"):
            confidences.append(video.confidence)
        if audio and hasattr(audio, "confidence"):
            confidences.append(audio.confidence)
        return sum(confidences) / len(confidences) if confidences else 0.7

    def _build_model_breakdown(self, image, video, audio, threat, metadata, screenshot, signals) -> dict:
        """Build per-model score breakdown for transparency."""
        breakdown = {}

        if image:
            breakdown["image"] = {
                "manipulation_score": image.manipulation_score,
                "classification": image.classification,
                "confidence": image.confidence,
                "risk_value": signals.get("image", 0),
                "models": image.evidence,
                "models_used": image.models_used,
            }

        if video:
            breakdown["video"] = {
                "authenticity_score": video.video_authenticity_score,
                "classification": video.classification,
                "confidence": video.confidence,
                "risk_value": signals.get("video", 0),
                "suspicious_frames": video.evidence.get("suspicious_frame_count", 0),
                "total_frames": video.evidence.get("total_frames_analyzed", 0),
                "models_used": video.models_used,
            }

        if audio:
            breakdown["audio"] = {
                "authenticity_score": audio.audio_authenticity_score,
                "voice_clone_detected": audio.voice_clone_detected,
                "classification": audio.classification,
                "confidence": audio.confidence,
                "risk_value": signals.get("audio", 0),
                "transcript": audio.transcript,
                "models_used": audio.models_used,
            }

        if threat:
            breakdown["threat"] = {
                "threat_score": threat.threat_score,
                "is_malicious": threat.is_malicious,
                "risk_value": signals.get("threat", 0),
                "vendors": [
                    {"name": v.vendor, "score": v.threat_score, "flagged": v.is_flagged, "details": v.details}
                    for v in threat.vendors
                ],
            }

        if metadata:
            breakdown["metadata"] = {
                "risk_score": metadata.risk_score,
                "editing_detected": metadata.editing_detected,
                "risk_value": signals.get("metadata", 0),
                "findings": metadata.findings,
                "device_info": metadata.device_info,
                "exif_summary": metadata.exif_summary,
            }

        if screenshot:
            breakdown["screenshot"] = {
                "risk_score": screenshot.risk_score,
                "is_screenshot": screenshot.is_screenshot,
                "risk_value": signals.get("screenshot", 0),
                "findings": screenshot.findings,
                "artifacts": screenshot.artifacts,
            }

        breakdown["signal_weights"] = {
            k: self.WEIGHTS[k] for k in signals
        }
        breakdown["available_signals"] = list(signals.keys())

        return breakdown

    def _build_evidence_report(self, trust_score, verdict, signals, image, video, audio, threat, metadata, screenshot) -> dict:
        """Build the evidence report for explainability."""
        findings = []
        all_artifacts = []

        # Image findings
        if image and "image" in signals:
            if image.classification == "fake":
                findings.append({
                    "signal": "Image Analysis",
                    "severity": "high",
                    "message": f"Face manipulation detected (score: {image.manipulation_score:.1%})",
                    "models": image.models_used,
                })
            else:
                findings.append({
                    "signal": "Image Analysis",
                    "severity": "low",
                    "message": f"No face manipulation detected (score: {image.manipulation_score:.1%})",
                    "models": image.models_used,
                })
            all_artifacts.extend(image.evidence.get("artifacts", []))

        # Video findings
        if video and "video" in signals:
            if video.classification == "manipulated":
                suspicious = video.evidence.get("suspicious_frame_count", 0)
                findings.append({
                    "signal": "Video Analysis",
                    "severity": "high",
                    "message": f"Temporal manipulation detected across {suspicious} frames",
                    "models": video.models_used,
                })
            else:
                findings.append({
                    "signal": "Video Analysis",
                    "severity": "low",
                    "message": "Temporal consistency maintained — no manipulation detected",
                    "models": video.models_used,
                })
            all_artifacts.extend(video.evidence.get("artifacts", []))

        # Audio findings
        if audio and "audio" in signals:
            if audio.voice_clone_detected:
                findings.append({
                    "signal": "Audio Analysis",
                    "severity": "high",
                    "message": f"Voice clone detected (authenticity: {audio.audio_authenticity_score:.1%})",
                    "models": audio.models_used,
                })
            else:
                findings.append({
                    "signal": "Audio Analysis",
                    "severity": "low",
                    "message": f"Voice appears authentic (authenticity: {audio.audio_authenticity_score:.1%})",
                    "models": audio.models_used,
                })
            all_artifacts.extend(audio.evidence.get("artifacts", []))

        # Threat findings
        if threat and "threat" in signals:
            if threat.is_malicious:
                flagged = [v.vendor for v in threat.vendors if v.is_flagged]
                findings.append({
                    "signal": "Threat Intelligence",
                    "severity": "high",
                    "message": f"URL flagged as malicious by: {', '.join(flagged)}",
                    "vendors": flagged,
                })
            else:
                findings.append({
                    "signal": "Threat Intelligence",
                    "severity": "low",
                    "message": "No threats detected from security vendors",
                })

        # Metadata Forensics findings
        if metadata and "metadata" in signals:
            high_meta = [f for f in metadata.findings if f.get("severity") == "high"]
            if high_meta:
                for f in high_meta:
                    findings.append({
                        "signal": "Metadata Forensics",
                        "severity": "high",
                        "message": f"{f['message']}",
                        "detail": f.get("detail", ""),
                    })
            elif metadata.editing_detected:
                findings.append({
                    "signal": "Metadata Forensics",
                    "severity": "medium",
                    "message": f"Editing software detected in metadata (risk: {metadata.risk_score:.0%})",
                })
            else:
                findings.append({
                    "signal": "Metadata Forensics",
                    "severity": "low",
                    "message": f"Metadata appears clean (risk: {metadata.risk_score:.0%})",
                })
            all_artifacts.extend(f"[Metadata] {f['message']}" for f in high_meta)

        # Screenshot Forensics findings
        if screenshot and "screenshot" in signals:
            high_ss = [f for f in screenshot.findings if f.get("severity") == "high"]
            if high_ss:
                for f in high_ss:
                    findings.append({
                        "signal": "Screenshot Forensics",
                        "severity": "high",
                        "message": f"{f['message']}",
                        "detail": f.get("detail", ""),
                    })
            elif screenshot.is_screenshot:
                findings.append({
                    "signal": "Screenshot Forensics",
                    "severity": "info",
                    "message": f"Screenshot detected with {len(screenshot.findings)} analysis checks (risk: {screenshot.risk_score:.0%})",
                })
            else:
                findings.append({
                    "signal": "Screenshot Forensics",
                    "severity": "low",
                    "message": f"No screenshot manipulation detected (risk: {screenshot.risk_score:.0%})",
                })
            all_artifacts.extend(f"[Screenshot] {a}" for a in screenshot.artifacts)

        # Build summary
        high_findings = [f for f in findings if f["severity"] == "high"]
        low_findings = [f for f in findings if f["severity"] == "low"]

        summary = self._generate_summary(verdict, high_findings, low_findings, trust_score)

        return {
            "trust_score": trust_score,
            "verdict": verdict,
            "summary_en": summary["en"],
            "summary_hi": summary["hi"],
            "findings": findings,
            "artifacts": all_artifacts[:10],  # Top 10 artifacts
            "signals_analyzed": list(signals.keys()),
            "analysis_completeness": f"{len(signals)}/{len(self.WEIGHTS)} signals available",
        }

    def _generate_summary(self, verdict, high_findings, low_findings, score) -> dict:
        """Generate plain-language summary in Hindi and English."""
        if verdict == "HIGH_TRUST":
            return {
                "en": f"Trust Score: {score}/100 — This media appears to be AUTHENTIC. All {len(low_findings)} checks passed with no manipulation indicators found.",
                "hi": f"विश्वास स्कोर: {score}/100 — यह मीडिया प्रामाणिक प्रतीत होता है। सभी {len(low_findings)} जाँचें पास हुईं, कोई हेरफेर का संकेत नहीं मिला।",
            }
        elif verdict == "UNCERTAIN":
            return {
                "en": f"Trust Score: {score}/100 — The authenticity of this media is UNCERTAIN. {len(high_findings)} concern(s) found. Further verification recommended.",
                "hi": f"विश्वास स्कोर: {score}/100 — इस मीडिया की प्रामाणिकता अनिश्चित है। {len(high_findings)} चिंता(एं) मिलीं। आगे सत्यापन की सिफारिश की जाती है।",
            }
        else:
            concerns = "; ".join(f["message"] for f in high_findings[:3])
            return {
                "en": f"Trust Score: {score}/100 — WARNING: This media shows signs of MANIPULATION. {len(high_findings)} red flag(s) detected: {concerns}. Do not share.",
                "hi": f"विश्वास स्कोर: {score}/100 — चेतावनी: इस मीडिया में हेरफेर के संकेत हैं। {len(high_findings)} खतरा(एं) मिला: {concerns}. साझा न करें।",
            }
