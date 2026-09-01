"""
SatyaKavach - Gemini Evidence Report Service
Uses Google Gemini 2.5 Flash to generate plain-language, explainable
evidence reports in Hindi and English for every verification verdict.

Features:
- Hindi-first bilingual reports
- Cites specific signals and artifacts
- Recommends clear actions
- Graceful fallback to template reports if API is unavailable
"""

import logging
import json
from dataclasses import dataclass, field
from typing import Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid crash if SDK not installed
_genai = None


def _get_genai():
    """Lazy-load google.generativeai."""
    global _genai
    if _genai is None:
        try:
            import google.generativeai as genai
            _genai = genai
        except ImportError:
            logger.warning("google-generativeai not installed. Run: pip install google-generativeai")
            return None
    return _genai


@dataclass
class EvidenceReport:
    """AI-generated evidence report."""
    summary_en: str
    summary_hi: str
    key_findings: list[dict] = field(default_factory=list)
    recommendation_en: str = ""
    recommendation_hi: str = ""
    explanation_en: str = ""
    explanation_hi: str = ""
    raw_response: str = ""
    is_ai_generated: bool = False


class GeminiEvidenceService:
    """Generate explainable evidence reports using Gemini 2.5 Flash."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL  # gemini-2.5-flash
        self._configured = False

    def _configure(self):
        """Configure Gemini API."""
        if self._configured:
            return True
        genai = _get_genai()
        if genai is None or not self.api_key:
            return False
        try:
            genai.configure(api_key=self.api_key)
            self._configured = True
            return True
        except Exception as e:
            logger.error(f"Gemini configuration failed: {e}")
            return False

    async def generate_report(
        self,
        trust_score: int,
        verdict: str,
        media_type: str,
        signals: dict[str, Any],
        model_breakdown: dict[str, Any],
        language: str = "both",
    ) -> EvidenceReport:
        """
        Generate an AI-powered evidence report.

        Args:
            trust_score: 0-100 trust score
            verdict: HIGH_TRUST / UNCERTAIN / LOW_TRUST
            media_type: image / video / audio / link / screenshot
            signals: Raw signal values {signal_name: risk_value}
            model_breakdown: Per-model score breakdown
            language: "en", "hi", or "both"
        """
        if not self._configure():
            logger.info("Gemini not available, using template report")
            return self._template_report(trust_score, verdict, media_type, signals)

        genai = _get_genai()

        # Build the analysis context
        context = self._build_context(trust_score, verdict, media_type, signals, model_breakdown)

        # Generate report
        try:
            model = genai.GenerativeModel(self.model_name)
            response = await model.generate_content_async(
                context,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                    top_p=0.8,
                ),
            )

            raw_text = response.text
            report = self._parse_response(raw_text, trust_score, verdict)
            report.is_ai_generated = True
            report.raw_response = raw_text

            logger.info(f"Gemini report generated for {media_type} (trust: {trust_score})")
            return report

        except Exception as e:
            logger.error(f"Gemini report generation failed: {e}")
            return self._template_report(trust_score, verdict, media_type, signals)

    def _build_context(
        self,
        trust_score: int,
        verdict: str,
        media_type: str,
        signals: dict[str, Any],
        model_breakdown: dict[str, Any],
    ) -> str:
        """Build the prompt context for Gemini."""

        # Format signals nicely
        signal_lines = []
        for name, value in signals.items():
            risk_pct = f"{value * 100:.1f}%"
            signal_lines.append(f"  - {name}: risk = {risk_pct}")

        # Format model breakdown
        model_lines = []
        for model_name, data in model_breakdown.items():
            if isinstance(data, dict) and "risk_value" in data:
                model_lines.append(f"  - {model_name}: risk={data['risk_value']:.3f}, details={data.get('models', data.get('details', 'N/A'))}")

        findings_text = "\n".join(signal_lines) if signal_lines else "  No signals available"
        models_text = "\n".join(model_lines) if model_lines else "  No model details"

        prompt = f"""You are SatyaKavach, an AI-powered media verification system for Indian citizens.

ANALYSIS RESULTS:
- Media Type: {media_type}
- Trust Score: {trust_score}/100
- Verdict: {verdict}

SIGNAL ANALYSIS:
{findings_text}

MODEL BREAKDOWN:
{models_text}

TASK: Generate a clear, plain-language evidence report for the citizen.

IMPORTANT: Output ONLY valid JSON. No markdown, no code blocks, no extra text.
All string values must be on a single line (no line breaks inside strings).
Keep each field under 150 characters.

OUTPUT THIS JSON:
{{"summary_en":"One sentence English summary","summary_hi":"One sentence Hindi summary","recommendation_en":"What to do next in English","recommendation_hi":"What to do next in Hindi","explanation_en":"Why this verdict in English","explanation_hi":"Why this verdict in Hindi"}}

RULES:
- Simple language (6th grade reading level)
- Hindi must be natural, not machine-translated
- Never say AI detected — say analysis found or patterns indicate
- LOW_TRUST: be firm about not sharing
- HIGH_TRUST: be reassuring
- UNCERTAIN: encourage cross-checking"""

        return prompt

    def _parse_response(self, raw_text: str, trust_score: int, verdict: str) -> EvidenceReport:
        """Parse Gemini's JSON response into an EvidenceReport."""
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                # Remove opening ```json or ```
                first_line_end = cleaned.find("\n")
                if first_line_end > 0:
                    cleaned = cleaned[first_line_end + 1:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            # Try to find JSON object boundaries
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start >= 0 and end > start:
                cleaned = cleaned[start:end + 1]

            data = json.loads(cleaned)

            return EvidenceReport(
                summary_en=data.get("summary_en", ""),
                summary_hi=data.get("summary_hi", ""),
                key_findings=data.get("key_findings", []),
                recommendation_en=data.get("recommendation_en", ""),
                recommendation_hi=data.get("recommendation_hi", ""),
                explanation_en=data.get("explanation_en", ""),
                explanation_hi=data.get("explanation_hi", ""),
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse Gemini response as JSON: {e}")
            # Try regex extraction as fallback
            return self._regex_fallback(raw_text, trust_score, verdict)

    def _regex_fallback(self, raw_text: str, trust_score: int, verdict: str) -> EvidenceReport:
        """Extract fields from Gemini response using regex when JSON parsing fails."""
        import re

        def extract_field(text, key):
            # Try: "key": "value" or "key": "value"
            pattern = f'"{key}"\s*:\s*"([^"]*?)"'
            match = re.search(pattern, text)
            if match:
                return match.group(1)
            # Try with escaped quotes
            pattern2 = f'"{key}"\s*:\s*"([^"]*?)"'
            match2 = re.search(pattern2, text)
            return match2.group(1) if match2 else ""

        findings = []
        finding_matches = re.findall(r'"finding_en"\s*:\s*"([^"]+)"', raw_text)
        finding_hi_matches = re.findall(r'"finding_hi"\s*:\s*"([^"]+)"', raw_text)
        severity_matches = re.findall(r'"severity"\s*:\s*"([^"]+)"', raw_text)
        for i, fen in enumerate(finding_matches):
            findings.append({
                "finding_en": fen,
                "finding_hi": finding_hi_matches[i] if i < len(finding_hi_matches) else "",
                "severity": severity_matches[i] if i < len(severity_matches) else "medium",
            })

        return EvidenceReport(
            summary_en=extract_field(raw_text, "summary_en") or raw_text[:200],
            summary_hi=extract_field(raw_text, "summary_hi"),
            key_findings=findings,
            recommendation_en=extract_field(raw_text, "recommendation_en"),
            recommendation_hi=extract_field(raw_text, "recommendation_hi"),
            explanation_en=extract_field(raw_text, "explanation_en"),
            explanation_hi=extract_field(raw_text, "explanation_hi"),
            raw_response=raw_text,
        )

    def _template_report(
        self,
        trust_score: int,
        verdict: str,
        media_type: str,
        signals: dict[str, Any],
    ) -> EvidenceReport:
        """Fallback template report when Gemini is unavailable."""
        signal_list = ", ".join(signals.keys()) if signals else "none"
        signal_count = len(signals)

        if verdict == "HIGH_TRUST":
            return EvidenceReport(
                summary_en=f"Trust Score: {trust_score}/100 — This {media_type} appears to be AUTHENTIC. Analysis of {signal_count} signal(s) ({signal_list}) found no manipulation indicators.",
                summary_hi=f"विश्वास स्कोर: {trust_score}/100 — यह {media_type} प्रामाणिक प्रतीत होता है। {signal_count} संकेत ({signal_list}) का विश्लेषण करने पर कोई हेरफेर नहीं मिला।",
                key_findings=[{"finding_en": "No manipulation detected", "finding_hi": "कोई हेरफेर नहीं मिला", "severity": "low"}],
                recommendation_en="You may share this media, but always verify the source and context.",
                recommendation_hi="आप इस मीडिया को साझा कर सकते हैं, लेकिन हमेशा स्रोत और संदर्भ सत्यापित करें।",
                explanation_en=f"Analysis of {signal_count} signal(s) found consistent patterns with authentic media. No editing artifacts, compression anomalies, or manipulation signatures were detected.",
                explanation_hi=f"{signal_count} संकेतों का विश्लेषण में प्रामाणिक मीडिया के साथ संगत पैटर्न मिले। कोई संपादन कलाकृति, संपीड़न विसंगतियाँ, या हेरफेर हस्ताक्षर नहीं मिले।",
            )
        elif verdict == "UNCERTAIN":
            return EvidenceReport(
                summary_en=f"Trust Score: {trust_score}/100 — The authenticity of this {media_type} is UNCERTAIN. Mixed signals detected across {signal_count} analysis(s).",
                summary_hi=f"विश्वास स्कोर: {trust_score}/100 — इस {media_type} की प्रामाणिकता अनिश्चित है। {signal_count} विश्लेषण में मिश्रित संकेत मिले।",
                key_findings=[{"finding_en": "Inconclusive results — some signals pass, some show concern", "finding_hi": "अनिर्णायक परिणाम — कुछ संकेत पास, कुछ चिंताजनक", "severity": "medium"}],
                recommendation_en="Further verification recommended. Cross-check with other sources before sharing.",
                recommendation_hi="आगे सत्यापन की सिफारिश की जाती है। साझा करने से पहले अन्य स्रोतों से जांचें।",
                explanation_en=f"Analysis found mixed signals. Some indicators suggest authenticity while others raise concerns. This could be due to re-compression, editing without manipulation, or inconclusive detection.",
                explanation_hi=f"विश्लेषण में मिश्रित संकेत मिले। कुछ संकेतक प्रामाणिकता का संकेत देते हैं जबकि अन्य चिंता जगाते हैं। यह पुनः संपीड़न, बिना हेरफेर के संपादन, या अनिर्णायक पहचान के कारण हो सकता है।",
            )
        else:
            return EvidenceReport(
                summary_en=f"Trust Score: {trust_score}/100 — WARNING: This {media_type} shows signs of MANIPULATION. {signal_count} signal(s) analyzed ({signal_list}).",
                summary_hi=f"विश्वास स्कोर: {trust_score}/100 — चेतावनी: इस {media_type} में हेरफेर के संकेत हैं। {signal_count} संकेतों का विश्लेषण किया गया ({signal_list})।",
                key_findings=[{"finding_en": "Manipulation indicators detected — do not share", "finding_hi": "हेरफेर संकेतक मिले — साझा न करें", "severity": "high"}],
                recommendation_en="DO NOT share this media. Report to I4C/1930 (Cyber Crime Helpline: 1930) if it involves fraud or impersonation.",
                recommendation_hi="इस मीडिया को साझा न करें। यदि यह धोखाधड़ी या प्रतिरूपण से संबंधित है तो I4C/1930 (साइबर अपराध हेल्पलाइन: 1930) पर रिपोर्ट करें।",
                explanation_en=f"Multiple analysis signals indicate this {media_type} has been manipulated or fabricated. The combination of {signal_count} detection method(s) consistently flags manipulation patterns.",
                explanation_hi=f"कई विश्लेषण संकेत इंगित करते हैं कि इस {media_type} में हेरफेर या नकली बनाया गया है। {signal_count} पहचान विधि(ओं) का संयोजन लगातार हेरफेर पैटर्न को चिन्हित करता है।",
            )
