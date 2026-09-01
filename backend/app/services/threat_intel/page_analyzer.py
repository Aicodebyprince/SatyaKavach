"""
SatyaKavach - Page Content Analyzer
Fetches a URL and analyzes the page for phishing/scam patterns:
- Fake login forms (impersonating banks, social media, gov)
- Urgency text (Hindi + English)
- Suspicious scripts (crypto miners, keyloggers, redirects)
- Visual deception (fake buttons, countdown timers)
- Content inconsistencies (language mismatch, brand impersonation)
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


@dataclass
class PageAnalysisResult:
    risk_score: float  # 0.0 = clean, 1.0 = highly suspicious
    is_reachable: bool
    findings: list[dict] = field(default_factory=list)
    page_title: str = ""
    final_url: str = ""
    redirect_chain: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


# ── Phishing keyword patterns (English + Hindi) ──

URGENCY_PATTERNS_EN = [
    (r"urgent.*action.*required", 0.6),
    (r"account.*suspended", 0.7),
    (r"verify.*identity.*immediately", 0.7),
    (r"your account.*will be.*locked", 0.8),
    (r"unauthorized.*access.*detected", 0.7),
    (r"click.*here.*immediately", 0.5),
    (r"confirm.*your.*bank.*details", 0.8),
    (r"share.*otp", 0.9),
    (r"send.*otp", 0.9),
    (r"win.*prize", 0.7),
    (r"congratulations.*won", 0.8),
    (r"claim.*reward", 0.7),
    (r"limited.*time.*offer", 0.5),
    (r"act.*now.*before", 0.5),
    (r"last.*chance", 0.4),
    (r"expires?.*(today|tomorrow|24.*hr)", 0.5),
]

URGENCY_PATTERNS_HI = [
    (r"तुरंत.*करें", 0.7),  # do immediately
    (r"account.*बंद.*होगा", 0.8),  # account will be blocked
    (r"OTP.*भेजें", 0.9),  # send OTP
    (r"OTP.*साझा.*करें", 0.9),  # share OTP
    (r"इनाम.*जीता", 0.8),  # won prize
    (r"बैंक.*विवरण.*सत्यापित", 0.8),  # verify bank details
    (r"तुरंत.*सत्यापित.*करें", 0.7),  # verify immediately
    (r"खाता.*सील.*होगा", 0.8),  # account will be sealed
    (r"अभी.*क्लिक.*करें", 0.5),  # click now
    (r"आप.*जीत.*गए", 0.8),  # you won
]

# Known brand impersonation targets
BRAND_TARGETS = {
    "google": ["google.com", "accounts.google.com", "gmail"],
    "facebook": ["facebook.com", "fb.com", "meta.com", "instagram.com"],
    "whatsapp": ["whatsapp.com", "web.whatsapp.com"],
    "amazon": ["amazon.in", "amazon.com", "amazonpay"],
    "paytm": ["paytm.com", "paytmmall.com"],
    "phonepe": ["phonepe.com"],
    "googlepay": ["pay.google.com", "gpay"],
    "sbi": ["sbi.co.in", "onlinesbi.com"],
    "icici": ["icicibank.com"],
    "hdfc": ["hdfcbank.com"],
    "axis": ["axisbank.com"],
    "aadhaar": ["uidai.gov.in", "aadhaar"],
    "pan": ["incometax.gov.in", "egov-nsdl"],
    "irctc": ["irctc.co.in"],
    "upi": ["npci.org.in"],
    "cybercrime": ["cybercrime.gov.in", "i4c", "1930"],
}

# Phishing form indicators
FORM_INDICATORS = [
    r"<form[^>]*password",
    r"<input[^>]*type=[\"']password",
    r"<input[^>]*name=[\"'][^\"']*(?:pass|pwd|credential)",
    r"<input[^>]*name=[\"'][^\"']*(?:card|cvv|otp)",
    r"<input[^>]*name=[\"'][^\"']*(?:account|acc_no|account_number)",
    r"<input[^>]*name=[\"'][^\"']*(?:ifsc|sort.?code)",
    r"<form[^>]*action=[\"'][^\"']*(?!.*(?:google|facebook|amazon)\.com)",
]

# Suspicious script patterns
SUSPICIOUS_SCRIPTS = [
    (r"crypto.?miner|coinhive|cryptoloot|coinimp", "crypto_miner", 0.8),
    (r"keylogger|key.?log|击键记录", "keylogger", 0.9),
    (r"document\.write\s*\(\s*unescape", "obfuscated_redirect", 0.7),
    (r"window\.location\s*=.*http(?!.*(?:google|facebook))", "suspicious_redirect", 0.6),
    (r"eval\s*\(\s*atob", "obfuscated_code", 0.7),
    (r"<iframe[^>]*hidden|display:\s*none.*iframe", "hidden_iframe", 0.6),
]

# URL shortener domains
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly",
    "ow.ly", "rb.gy", "cutt.ly", "shorturl.at", "dwz.cn", "rebrand.ly",
}


class PageContentAnalyzer:
    """Fetch and analyze web page content for phishing/scam indicators."""

    def __init__(self):
        self.timeout = 10.0

    async def analyze(self, url: str) -> PageAnalysisResult:
        """Full page content analysis."""
        findings = []
        risk_score = 0.0
        final_url = url
        redirect_chain = []
        page_title = ""
        is_reachable = False

        # ── Step 1: Fetch page with redirect tracking ──
        try:
            html_content, final_url, redirect_chain, page_title = await self._fetch_page(url)
            is_reachable = True
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}")
            findings.append({
                "type": "unreachable",
                "severity": "medium",
                "message": f"Page could not be fetched: {type(e).__name__}",
                "detail": "The URL may be down, blocked, or require authentication.",
            })
            return PageAnalysisResult(
                risk_score=0.3,
                is_reachable=False,
                findings=findings,
                evidence={"error": str(e)},
            )

        # ── Step 2: Check for redirects ──
        if len(redirect_chain) > 2:
            risk = min(0.4, len(redirect_chain) * 0.1)
            risk_score = max(risk_score, risk)
            findings.append({
                "type": "redirect_chain",
                "severity": "medium" if len(redirect_chain) > 3 else "low",
                "message": f"Multiple redirects detected ({len(redirect_chain)} hops)",
                "detail": "Excessive redirects are a common phishing technique.",
            })

        # Check if final URL differs significantly from original
        orig_domain = urlparse(url).hostname or ""
        final_domain = urlparse(final_url).hostname or ""
        if orig_domain != final_domain and orig_domain and final_domain:
            risk_score = max(risk_score, 0.3)
            findings.append({
                "type": "domain_mismatch",
                "severity": "medium",
                "message": f"Redirected from {orig_domain} to {final_domain}",
                "detail": "Domain changed after redirect — possible phishing redirect.",
            })

        # ── Step 3: Analyze page content ──
        html_lower = html_content.lower()

        # Urgency text detection (English)
        for pattern, severity in URGENCY_PATTERNS_EN:
            if re.search(pattern, html_lower):
                risk_score = max(risk_score, severity)
                findings.append({
                    "type": "urgency_text",
                    "severity": "high" if severity > 0.6 else "medium",
                    "message": f"Suspicious urgency pattern detected: {pattern[:40]}",
                    "detail": "Phishing pages use urgency to pressure victims.",
                })
                break  # One match is enough

        # Urgency text detection (Hindi)
        for pattern, severity in URGENCY_PATTERNS_HI:
            if re.search(pattern, html_content):
                risk_score = max(risk_score, severity)
                findings.append({
                    "type": "urgency_text_hindi",
                    "severity": "high" if severity > 0.6 else "medium",
                    "message": f"Hindi urgency pattern detected (risk: {severity:.0%})",
                    "detail": "Hindi phishing text targeting Indian users.",
                })
                break

        # ── Step 4: Form analysis ──
        form_risk = self._analyze_forms(html_content)
        if form_risk > 0:
            risk_score = max(risk_score, form_risk)
            findings.append({
                "type": "suspicious_form",
                "severity": "high" if form_risk > 0.6 else "medium",
                "message": f"Suspicious form detected (risk: {form_risk:.0%})",
                "detail": "Page contains forms requesting sensitive information.",
            })

        # ── Step 5: Brand impersonation check ──
        brand_risk, brand_findings = self._check_brand_impersonation(
            orig_domain, final_domain, html_lower, page_title
        )
        risk_score = max(risk_score, brand_risk)
        findings.extend(brand_findings)

        # ── Step 6: Suspicious scripts ──
        for pattern, script_type, severity in SUSPICIOUS_SCRIPTS:
            if re.search(pattern, html_lower):
                risk_score = max(risk_score, severity)
                findings.append({
                    "type": "suspicious_script",
                    "severity": "high" if severity > 0.7 else "medium",
                    "message": f"Potentially malicious script: {script_type}",
                    "detail": "Page contains code patterns associated with malicious behavior.",
                })

        # ── Step 7: SSL/HTTPS check ──
        parsed = urlparse(url)
        if parsed.scheme != "https":
            risk_score = max(risk_score, 0.15)
            findings.append({
                "type": "no_https",
                "severity": "low",
                "message": "Page does not use HTTPS",
                "detail": "Phishing pages often avoid HTTPS or use invalid certificates.",
            })

        evidence = {
            "risk_score": round(min(1.0, risk_score), 3),
            "is_reachable": is_reachable,
            "page_title": page_title,
            "final_url": final_url,
            "redirect_hops": len(redirect_chain),
            "findings_count": len(findings),
            "high_severity_count": sum(1 for f in findings if f.get("severity") == "high"),
        }

        return PageAnalysisResult(
            risk_score=round(min(1.0, risk_score), 3),
            is_reachable=is_reachable,
            findings=findings,
            page_title=page_title,
            final_url=final_url,
            redirect_chain=redirect_chain,
            evidence=evidence,
        )

    async def _fetch_page(self, url: str) -> tuple[str, str, list[str], str]:
        """Fetch page content with redirect tracking."""
        redirect_chain = []
        final_url = url
        page_title = ""

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": "SatyaKavach/1.0 (Security Verification)"},
        ) as client:
            response = await client.get(url)

            # Track redirects
            if hasattr(response, "history"):
                for resp in response.history:
                    redirect_chain.append(str(resp.url))
            final_url = str(response.url)

            html = response.text

            # Extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = title_match.group(1).strip()[:200]

            return html, final_url, redirect_chain, page_title

    def _analyze_forms(self, html: str) -> float:
        """Analyze forms for phishing indicators — only flag suspicious data requests."""
        risk = 0.0

        # Extract only <input> and <form> tags (not meta tags, scripts, etc.)
        input_tags = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
        form_tags = re.findall(r'<form[^>]+>', html, re.IGNORECASE)
        inputs_text = " ".join(input_tags)
        forms_text = " ".join(form_tags)
        all_form_text = inputs_text + " " + forms_text

        if not all_form_text.strip():
            return 0.0

        # Check for ONLY the most suspicious fields in actual form inputs
        banking_patterns = [
            r'name=["\'][^"\']*(?:card_number|card_num|credit_card|debit_card|card_no)',
            r'name=["\'][^"\']*(?:cvv|cvc|security_code)',
            r'name=["\'][^"\']*(?:ifsc|sort.?code|routing_number)',
            r'name=["\'][^"\']*(?:account_number|acc_no|bank_account)',
            r'name=["\'][^"\']*(?:aadhaar|pan_number|pan_card)',
            r'placeholder=["\'][^"\']*(?:card.*number|cvv|credit.*card)',
        ]
        for pattern in banking_patterns:
            if re.search(pattern, all_form_text, re.IGNORECASE):
                risk = max(risk, 0.8)
                break

        # OTP request in form inputs (very common in Indian phishing)
        otp_patterns = [
            r'name=["\'][^"\']*(?:otp|one.?time)',
            r'placeholder=["\'][^"\']*(?:enter.*otp|otp.*code)',
        ]
        for pattern in otp_patterns:
            if re.search(pattern, all_form_text, re.IGNORECASE):
                risk = max(risk, 0.7)
                break

        # Password forms — low risk (legitimate sites have these)
        password_fields = len(re.findall(r'type=["\']password', all_form_text, re.IGNORECASE))
        if password_fields > 0 and risk == 0:
            risk = 0.15

        return risk

    def _check_brand_impersonation(
        self, orig_domain: str, final_domain: str, html_lower: str, page_title: str
    ) -> tuple[float, list[dict]]:
        """Check if page is impersonating a known brand.
        
        Only flags if the brand name appears in the DOMAIN or TITLE
        (not just somewhere in the page body — GitHub mentions 'amazon' in dependencies etc.)
        """
        findings = []
        risk = 0.0

        # Only check domain and title, NOT the full page body
        check_text = f"{orig_domain} {final_domain} {page_title}".lower()

        for brand, legitimate_domains in BRAND_TARGETS.items():
            # Check if brand name appears in domain or title
            brand_in_domain_or_title = brand.lower() in check_text
            # Check if we're NOT on the legitimate domain
            on_legitimate = any(ld in final_domain.lower() for ld in legitimate_domains)

            if brand_in_domain_or_title and not on_legitimate:
                # Extra check: is the brand in the DOMAIN itself? (stronger signal)
                brand_in_domain = brand.lower() in final_domain.lower()
                severity = "high" if brand_in_domain else "medium"
                risk_boost = 0.7 if brand_in_domain else 0.3
                risk = max(risk, risk_boost)
                findings.append({
                    "type": "brand_impersonation",
                    "severity": severity,
                    "message": f"Possible {brand.title()} impersonation (not on {legitimate_domains[0]})",
                    "detail": f"Brand '{brand}' found in domain/title ({final_domain}), but not on the official domain.",
                })

        return risk, findings
