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


class ThreatIntelligenceService:
    """External threat intelligence for URL/domain/file reputation."""

    def __init__(self):
        self.vt_api_key = settings.VIRUSTOTAL_API_KEY
        self.gsb_api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
        self.phishtank_key = settings.PHISHTANK_APP_KEY

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

        # Compute final threat score (max of all vendor scores)
        threat_score = max((v.threat_score for v in vendors), default=0.0)
        is_malicious = any(v.is_flagged for v in vendors)

        return ThreatVerdict(
            threat_score=round(threat_score, 3),
            is_malicious=is_malicious,
            vendors=vendors,
            evidence={
                "vendor_scores": {v.vendor: v.threat_score for v in vendors},
                "flagged_by": [v.vendor for v in vendors if v.is_flagged],
                "domain_analysis": domain_rep.details,
            },
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
        """Heuristic domain reputation check."""
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            score = 0.0
            reasons = []

            # Suspicious TLDs
            suspicious_tlds = [".xyz", ".top", ".club", ".buzz", ".info", ".tk", ".ml"]
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                score += 0.3
                reasons.append(f"Suspicious TLD")

            # Very long domain
            if len(domain) > 30:
                score += 0.2
                reasons.append("Unusually long domain name")

            # IP address instead of domain
            import re
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
                score += 0.4
                reasons.append("IP address used instead of domain name")

            # No HTTPS
            if parsed.scheme != "https":
                score += 0.1
                reasons.append("No HTTPS")

            # Suspicious keywords
            suspicious_words = ["login", "verify", "secure", "account", "banking", "update", "confirm"]
            if sum(1 for w in suspicious_words if w in domain.lower()) > 1:
                score += 0.2
                reasons.append("Suspicious keywords in domain")

            return VendorVerdict(
                vendor="domain_reputation",
                threat_score=round(min(1.0, score), 3),
                is_flagged=score > 0.5,
                details="; ".join(reasons) if reasons else "Domain appears normal",
            )
        except Exception:
            return VendorVerdict(vendor="domain_reputation", threat_score=0.0, is_flagged=False, details="Unable to analyze")
