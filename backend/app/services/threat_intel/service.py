"""
SatyaKavach - Threat Intelligence Service
Integrates: VirusTotal, Google Safe Browsing, PhishTank, Domain Reputation
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class VendorVerdict:
    vendor: str
    threat_score: float  # 0.0 = safe, 1.0 = malicious
    is_flagged: bool
    details: str = ""


@dataclass
class ThreatVerdict:
    threat_score: float  # 0.0 = safe, 1.0 = malicious
    is_malicious: bool
    vendors: list[VendorVerdict] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


from app.services.threat_intel.page_analyzer import PageContentAnalyzer, PageAnalysisResult


class ThreatIntelligenceService:
    """External threat intelligence for URL/domain/file reputation."""

    def __init__(self):
        self.vt_api_key = settings.VIRUSTOTAL_API_KEY
        self.gsb_api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
        self.phishtank_key = settings.PHISHTANK_APP_KEY
        self.page_analyzer = PageContentAnalyzer()

    async def analyze(self, url: str) -> ThreatVerdict:
        """Run full threat intelligence check on a URL."""
        if not url:
            return ThreatVerdict(threat_score=0.0, is_malicious=False)

        vendors = []

        # VirusTotal
        if self.vt_api_key:
            try:
                vt = await self._check_virustotal(url)
                vendors.append(vt)
            except Exception as e:
                logger.warning(f"VirusTotal check failed: {e}")
        else:
            vendors.append(VendorVerdict(
                vendor="virustotal",
                threat_score=0.0,
                is_flagged=False,
                details="API key not configured (demo mode)",
            ))

        # Google Safe Browsing
        if self.gsb_api_key:
            try:
                gsb = await self._check_safe_browsing(url)
                vendors.append(gsb)
            except Exception as e:
                logger.warning(f"Safe Browsing check failed: {e}")
        else:
            vendors.append(VendorVerdict(
                vendor="safe_browsing",
                threat_score=0.0,
                is_flagged=False,
                details="API key not configured (demo mode)",
            ))

        # PhishTank
        if self.phishtank_key:
            try:
                pt = await self._check_phishtank(url)
                vendors.append(pt)
            except Exception as e:
                logger.warning(f"PhishTank check failed: {e}")
        else:
            vendors.append(VendorVerdict(
                vendor="phishtank",
                threat_score=0.0,
                is_flagged=False,
                details="API key not configured (demo mode)",
            ))

        # Domain Reputation (heuristic)
        domain_rep = self._check_domain_reputation(url)
        vendors.append(domain_rep)

        # Page Content Analysis (fetch + analyze)
        page_result = None
        try:
            page_result = await self.page_analyzer.analyze(url)
            if page_result.risk_score > 0:
                vendors.append(VendorVerdict(
                    vendor="page_content",
                    threat_score=page_result.risk_score,
                    is_flagged=page_result.risk_score > 0.5,
                    details=self._format_page_findings(page_result.findings),
                ))
        except Exception as e:
            logger.warning(f"Page analysis failed for {url}: {e}")

        # Compute final threat score (max of all vendor scores)
        threat_score = max((v.threat_score for v in vendors), default=0.0)
        is_malicious = any(v.is_flagged for v in vendors)

        evidence = {
            "vendor_scores": {v.vendor: v.threat_score for v in vendors},
            "flagged_by": [v.vendor for v in vendors if v.is_flagged],
            "domain_analysis": domain_rep.details,
        }
        if page_result:
            evidence["page_analysis"] = {
                "risk_score": page_result.risk_score,
                "page_title": page_result.page_title,
                "final_url": page_result.final_url,
                "redirect_hops": len(page_result.redirect_chain),
                "findings": page_result.findings,
            }

        return ThreatVerdict(
            threat_score=round(threat_score, 3),
            is_malicious=is_malicious,
            vendors=vendors,
            evidence=evidence,
        )

    async def _check_virustotal(self, url: str) -> VendorVerdict:
        """Check URL against VirusTotal API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Encode URL for VT API
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            response = await client.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                headers={"x-apikey": self.vt_api_key},
            )
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                malicious_count = stats.get("malicious", 0)
                total_count = sum(stats.values()) or 1
                score = malicious_count / total_count
                return VendorVerdict(
                    vendor="virustotal",
                    threat_score=round(min(1.0, score * 2), 3),  # Amplify for sensitivity
                    is_flagged=malicious_count > 0,
                    details=f"{malicious_count}/{total_count} engines flagged",
                )
        return VendorVerdict(vendor="virustotal", threat_score=0.0, is_flagged=False, details="No data")

    async def _check_safe_browsing(self, url: str) -> VendorVerdict:
        """Check URL against Google Safe Browsing API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "client": {"clientId": "satyakavach", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}],
                },
            }
            response = await client.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.gsb_api_key}",
                json=payload,
            )
            if response.status_code == 200:
                matches = response.json().get("matches", [])
                if matches:
                    threat_types = [m.get("threatType", "") for m in matches]
                    return VendorVerdict(
                        vendor="safe_browsing",
                        threat_score=0.9,
                        is_flagged=True,
                        details=f"Threats detected: {', '.join(threat_types)}",
                    )
        return VendorVerdict(vendor="safe_browsing", threat_score=0.0, is_flagged=False, details="No threats found")

    async def _check_phishtank(self, url: str) -> VendorVerdict:
        """Check URL against PhishTank database."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "http://data.phishtank.com/data/online-valid.csv",
                timeout=30.0,
            )
            if response.status_code == 200:
                # Quick check if URL appears in the phishing database
                if url.encode() in response.content:
                    return VendorVerdict(
                        vendor="phishtank",
                        threat_score=0.95,
                        is_flagged=True,
                        details="URL found in PhishTank phishing database",
                    )
        return VendorVerdict(vendor="phishtank", threat_score=0.0, is_flagged=False, details="Not in database")

    def _check_domain_reputation(self, url: str) -> VendorVerdict:
        """Heuristic domain reputation check — enhanced with typosquatting, homoglyphs, shorteners."""
        try:
            import re
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            score = 0.0
            reasons = []

            # ── Suspicious TLDs ──
            suspicious_tlds = [
                ".xyz", ".top", ".club", ".buzz", ".info", ".tk", ".ml",
                ".ga", ".cf", ".gq", ".pw", ".cc", ".icu", ".cam",
                ".rest", ".support", ".click", ".link", ".download",
            ]
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                score += 0.3
                reasons.append("Suspicious TLD")

            # ── Very long domain ──
            if len(domain) > 30:
                score += 0.2
                reasons.append("Unusually long domain name")

            # ── IP address instead of domain ──
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
                score += 0.4
                reasons.append("IP address used instead of domain name")

            # ── No HTTPS ──
            if parsed.scheme != "https":
                score += 0.1
                reasons.append("No HTTPS")

            # ── Suspicious keywords in domain ──
            suspicious_words = [
                "login", "verify", "secure", "account", "banking", "update",
                "confirm", "auth", "signin", "wallet", "pay", "otp",
                "refund", "kyc", "aadhaar", "pan",
            ]
            keyword_hits = [w for w in suspicious_words if w in domain.lower()]
            if len(keyword_hits) > 1:
                score += 0.25
                reasons.append(f"Suspicious keywords: {', '.join(keyword_hits)}")
            elif len(keyword_hits) == 1:
                score += 0.1
                reasons.append(f"Keyword in domain: {keyword_hits[0]}")

            # ── URL shortener detection ──
            shortener_domains = {
                "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd",
                "buff.ly", "ow.ly", "rb.gy", "cutt.ly", "shorturl.at",
                "dwz.cn", "rebrand.ly", "bl.ink", "suo.im",
            }
            if domain in shortener_domains:
                score += 0.2
                reasons.append(f"URL shortener ({domain}) — actual destination hidden")

            # ── Homoglyph / IDN attack detection ──
            # Look for Cyrillic, Greek, or other look-alike characters
            suspicious_chars = set()
            for ch in domain:
                code = ord(ch)
                # Cyrillic look-alikes (а, е, о, р, с, etc.)
                if 0x0400 <= code <= 0x04FF:
                    suspicious_chars.add(ch)
                # Greek look-alikes (α, ε, ο, ρ, etc.)
                elif 0x0370 <= code <= 0x03FF:
                    suspicious_chars.add(ch)
            if suspicious_chars:
                score += 0.6
                reasons.append(f"Homoglyph attack: non-Latin chars {suspicious_chars} in domain")

            # ── Typosquatting detection ──
            known_brands = [
                "google", "facebook", "instagram", "whatsapp", "amazon",
                "paytm", "phonepe", "gpay", "sbi", "icici", "hdfc",
                "irctc", "uidai", "aadhaar", "pan",
            ]
            for brand in known_brands:
                if brand in domain.lower():
                    # Check if it's the exact brand domain
                    is_exact = domain.lower().endswith(f"{brand}.com") or \
                               domain.lower().endswith(f"{brand}.in") or \
                               domain.lower().endswith(f"{brand}.co.in")
                    if not is_exact and len(domain) > len(brand) + 4:
                        score += 0.3
                        reasons.append(f"Possible typosquatting of {brand.title()}")
                        break

            # ── Excessive subdomains (e.g., login.secure.verify.google.com) ──
            subdomain_count = len(domain.split(".")) - 1
            if subdomain_count > 3:
                score += 0.2
                reasons.append(f"Excessive subdomains ({subdomain_count} levels)")

            # ── Random-looking domain (high entropy) ──
            base_domain = domain.split(".")[0] if domain else ""
            if len(base_domain) > 8:
                # Calculate character diversity
                unique_chars = len(set(base_domain))
                char_ratio = unique_chars / len(base_domain)
                has_digits = any(c.isdigit() for c in base_domain)
                if char_ratio > 0.7 and has_digits and len(base_domain) > 12:
                    score += 0.15
                    reasons.append("Random-looking domain name (high entropy)")

            return VendorVerdict(
                vendor="domain_reputation",
                threat_score=round(min(1.0, score), 3),
                is_flagged=score > 0.5,
                details="; ".join(reasons) if reasons else "Domain appears normal",
            )
        except Exception:
            return VendorVerdict(vendor="domain_reputation", threat_score=0.0, is_flagged=False, details="Unable to analyze")

    @staticmethod
    def _format_page_findings(findings: list[dict]) -> str:
        """Format page analysis findings into a summary string."""
        high_medium = [f for f in findings if f.get("severity") in ("high", "medium")]
        if not high_medium:
            return f"{len(findings)} findings, all low severity"
        summaries = [f["message"] for f in high_medium[:5]]
        return f"{len(findings)} findings: {'; '.join(summaries)}"
