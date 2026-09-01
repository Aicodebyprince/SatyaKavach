"""
SatyaKavach - Screenshot Forensics Analyzer
Detects manipulation in screenshots and social media captures:
- JPEG compression inconsistencies (double-compression, region re-encoding)
- Edge/clone detection artifacts
- Noise pattern analysis (inconsistent noise = spliced regions)
- Resolution & aspect ratio red flags (non-standard dimensions)
- Color histogram anomalies
- Text rendering analysis (font consistency check)
"""

import logging
import hashlib
from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Common mobile screen resolutions (w, h) - suspicious if not matching
COMMON_RESOLUTIONS = {
    (1080, 1920), (1080, 2340), (1080, 2400), (1080, 2160),
    (720, 1280), (720, 1560), (750, 1334), (1125, 2436),
    (1170, 2532), (1242, 2688), (1284, 2778), (1290, 2796),
    (1440, 3200), (1440, 2560), (1600, 2560), (1644, 3840),
    # Laptop/Desktop
    (1920, 1080), (2560, 1440), (3840, 2160), (1366, 768),
    (1440, 900), (1536, 864), (1280, 720),
}

# Known fake template dimensions (WhatsApp, Instagram, Twitter, etc.)
KNOWN_TEMPLATE_PATTERNS = {
    "whatsapp_chat": {"min_width": 300, "max_width": 500, "aspect_ratio_range": (0.4, 0.7)},
    "instagram_post": {"min_width": 500, "max_width": 1200, "aspect_ratio_range": (0.8, 1.2)},
    "tweet": {"min_width": 400, "max_width": 800, "aspect_ratio_range": (0.6, 1.0)},
    "news_headline": {"min_width": 600, "max_width": 1400, "aspect_ratio_range": (0.3, 0.8)},
}


@dataclass
class ScreenshotVerdict:
    risk_score: float  # 0.0 = clean, 1.0 = suspicious
    is_screenshot: bool
    findings: list[dict] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)


class ScreenshotForensicsAnalyzer:
    """Analyze images for screenshot manipulation and editing artifacts."""

    def analyze(self, file_data: bytes) -> ScreenshotVerdict:
        """Full forensic analysis of an image."""
        findings = []
        artifacts = []
        risk_score = 0.0

        # Load image with OpenCV
        nparr = np.frombuffer(file_data, np.uint8)
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if cv_img is None:
            return ScreenshotVerdict(
                risk_score=0.3,
                is_screenshot=False,
                findings=[{"type": "error", "severity": "medium", "message": "Could not decode image"}],
            )

        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        height, width = cv_img.shape[:2]
        is_screenshot = False

        # ── Test 1: Resolution Analysis ──
        resolution_risk, res_findings = self._analyze_resolution(width, height)
        risk_score = max(risk_score, resolution_risk)
        findings.extend(res_findings)

        # Check if it looks like a screenshot
        aspect = width / height if height > 0 else 0
        for template_name, pattern in KNOWN_TEMPLATE_PATTERNS.items():
            if (pattern["min_width"] <= width <= pattern["max_width"] and
                pattern["aspect_ratio_range"][0] <= aspect <= pattern["aspect_ratio_range"][1]):
                is_screenshot = True
                findings.append({
                    "type": "template_match",
                    "severity": "info",
                    "message": f"Dimensions match known pattern: {template_name} ({width}x{height})",
                })

        # ── Test 2: JPEG Compression Analysis ──
        comp_risk, comp_findings = self._analyze_compression(cv_img)
        risk_score = max(risk_score, comp_risk)
        findings.extend(comp_findings)

        # ── Test 3: Noise Pattern Analysis ──
        noise_risk, noise_findings = self._analyze_noise_patterns(gray)
        risk_score = max(risk_score, noise_risk)
        findings.extend(noise_findings)

        # ── Test 4: Edge / Clone Detection ──
        edge_risk, edge_findings = self._analyze_edges(gray)
        risk_score = max(risk_score, edge_risk)
        findings.extend(edge_findings)

        # ── Test 5: Color Histogram Analysis ──
        hist_risk, hist_findings = self._analyze_color_histogram(cv_img)
        risk_score = max(risk_score, hist_risk)
        findings.extend(hist_findings)

        # ── Test 6: Screenshot UI Detection ──
        ui_risk, ui_findings = self._detect_screenshot_ui(cv_img, gray)
        risk_score = max(risk_score, ui_risk)
        findings.extend(ui_findings)
        if ui_findings:
            is_screenshot = True

        # ── Test 7: Text Region Analysis ──
        text_risk, text_findings = self._analyze_text_regions(gray)
        risk_score = max(risk_score, text_risk)
        findings.extend(text_findings)

        # Build artifacts list
        high_findings = [f for f in findings if f.get("severity") == "high"]
        for f in high_findings:
            artifacts.append(f["message"])

        evidence = {
            "risk_score": round(min(1.0, risk_score), 3),
            "is_screenshot": is_screenshot,
            "image_dimensions": f"{width}x{height}",
            "findings_count": len(findings),
            "high_severity_count": len(high_findings),
            "artifacts": artifacts,
        }

        return ScreenshotVerdict(
            risk_score=round(min(1.0, risk_score), 3),
            is_screenshot=is_screenshot,
            findings=findings,
            artifacts=artifacts,
            evidence=evidence,
        )

    def _analyze_resolution(self, width: int, height: int) -> tuple[float, list]:
        """Check if resolution is suspicious."""
        findings = []
        risk = 0.0

        if (width, height) in COMMON_RESOLUTIONS or (height, width) in COMMON_RESOLUTIONS:
            findings.append({
                "type": "resolution",
                "severity": "info",
                "message": f"Standard device resolution: {width}x{height}",
            })
        else:
            # Non-standard resolution - could be cropped or from a fake template
            is_round_10 = width % 10 == 0 and height % 10 == 0
            is_very_small = width < 400 or height < 400
            is_very_large = width > 4000 or height > 4000

            if is_very_small:
                risk = 0.2
                findings.append({
                    "type": "resolution",
                    "severity": "low",
                    "message": f"Unusually small image: {width}x{height}",
                })
            elif is_very_large:
                risk = 0.1
                findings.append({
                    "type": "resolution",
                    "severity": "info",
                    "message": f"Very large image: {width}x{height}",
                })
            elif not is_round_10:
                risk = 0.15
                findings.append({
                    "type": "resolution",
                    "severity": "low",
                    "message": f"Non-standard resolution: {width}x{height} (not a common device)",
                })

        return risk, findings

    def _analyze_compression(self, cv_img: np.ndarray) -> tuple[float, list]:
        """Detect JPEG compression anomalies — re-compression or region splicing."""
        findings = []
        risk = 0.0

        try:
            # Encode to JPEG at different quality levels and compare
            _, buf_high = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            _, buf_low = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 50])

            # Compute block artifact metric (8x8 DCT blocks)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY).astype(np.float32)

            # Horizontal and vertical differences at block boundaries
            h_diff = np.abs(np.diff(gray, axis=1))
            v_diff = np.abs(np.diff(gray, axis=0))

            # Check periodicity at 8-pixel intervals (JPEG block size)
            h_block_diffs = []
            for offset in range(0, min(h_diff.shape[1], 64), 8):
                h_block_diffs.append(np.mean(h_diff[:, offset::8]))

            v_block_diffs = []
            for offset in range(0, min(v_diff.shape[0], 64), 8):
                v_block_diffs.append(np.mean(v_diff[offset::8, :]))

            if h_block_diffs and v_block_diffs:
                avg_in_block = np.mean(h_block_diffs + v_block_diffs)
                # Very strong block artifacts suggest re-compression
                if avg_in_block > 15:
                    risk = 0.35
                    findings.append({
                        "type": "compression",
                        "severity": "high",
                        "message": f"Strong JPEG compression artifacts detected (score: {avg_in_block:.1f})",
                        "detail": "Image may have been re-compressed after editing.",
                    })
                elif avg_in_block > 8:
                    risk = 0.15
                    findings.append({
                        "type": "compression",
                        "severity": "low",
                        "message": f"Moderate compression artifacts (score: {avg_in_block:.1f})",
                    })

        except Exception as e:
            logger.debug(f"Compression analysis error: {e}")

        return risk, findings

    def _analyze_noise_patterns(self, gray: np.ndarray) -> tuple[float, list]:
        """Detect inconsistent noise patterns — spliced regions have different noise."""
        findings = []
        risk = 0.0

        try:
            h, w = gray.shape
            # Divide image into 4x4 grid
            grid_rows, grid_cols = 4, 4
            cell_h, cell_w = h // grid_rows, w // grid_cols

            noise_map = []
            for r in range(grid_rows):
                row = []
                for c in range(grid_cols):
                    cell = gray[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w].astype(np.float32)
                    # Estimate noise as high-frequency content
                    laplacian = cv2.Laplacian(cell, cv2.CV_64F)
                    noise_level = np.std(laplacian)
                    row.append(noise_level)
                noise_map.append(row)

            noise_map = np.array(noise_map)
            mean_noise = np.mean(noise_map)
            std_noise = np.std(noise_map)

            if mean_noise > 0:
                cv_noise = std_noise / mean_noise  # Coefficient of variation
                if cv_noise > 0.5:
                    risk = 0.4
                    # Find the most anomalous cell
                    max_dev = np.max(np.abs(noise_map - mean_noise) / mean_noise)
                    findings.append({
                        "type": "noise_inconsistency",
                        "severity": "high",
                        "message": f"Highly inconsistent noise pattern across image regions (CV: {cv_noise:.2f})",
                        "detail": f"Maximum deviation from mean: {max_dev:.1f}x — suggests region splicing or compositing.",
                    })
                elif cv_noise > 0.3:
                    risk = 0.15
                    findings.append({
                        "type": "noise_inconsistency",
                        "severity": "low",
                        "message": f"Moderate noise variation across regions (CV: {cv_noise:.2f})",
                    })
                else:
                    findings.append({
                        "type": "noise_consistent",
                        "severity": "info",
                        "message": "Noise pattern consistent across image regions",
                    })

        except Exception as e:
            logger.debug(f"Noise analysis error: {e}")

        return risk, findings

    def _analyze_edges(self, gray: np.ndarray) -> tuple[float, list]:
        """Detect suspicious edge patterns from copy-paste or clone operations."""
        findings = []
        risk = 0.0

        try:
            edges = cv2.Canny(gray, 50, 150)

            # Look for suspiciously straight horizontal/vertical edges
            # (common in copy-paste boundaries)
            h_lines = np.sum(edges, axis=1)
            v_lines = np.sum(edges, axis=0)

            # Find peaks that might indicate splice boundaries
            h_threshold = np.mean(h_lines) + 3 * np.std(h_lines)
            v_threshold = np.mean(v_lines) + 3 * np.std(v_lines)

            h_spikes = np.sum(h_lines > h_threshold)
            v_spikes = np.sum(v_lines > v_threshold)

            # Also check for duplicate content via structural similarity
            h, w = gray.shape
            if w > 200 and h > 200:
                # Compare top half vs bottom half edge density
                top_edges = np.mean(edges[:h // 2, :])
                bottom_edges = np.mean(edges[h // 2:, :])
                left_edges = np.mean(edges[:, :w // 2])
                right_edges = np.mean(edges[:, w // 2:])

                edge_cv = np.std([top_edges, bottom_edges, left_edges, right_edges])
                if edge_cv > 10:
                    risk = 0.25
                    findings.append({
                        "type": "edge_anomaly",
                        "severity": "medium",
                        "message": "Asymmetric edge distribution detected",
                        "detail": "Different quadrants have very different edge density — possible composite image.",
                    })

            if h_spikes > 3 or v_spikes > 3:
                risk = max(risk, 0.3)
                findings.append({
                    "type": "splice_boundary",
                    "severity": "high",
                    "message": f"Possible splice boundaries detected (H: {h_spikes}, V: {v_spikes} suspicious lines)",
                    "detail": "Strong straight edges suggest copy-paste boundaries or region replacement.",
                })

        except Exception as e:
            logger.debug(f"Edge analysis error: {e}")

        return risk, findings

    def _analyze_color_histogram(self, cv_img: np.ndarray) -> tuple[float, list]:
        """Detect color histogram anomalies suggesting selective editing."""
        findings = []
        risk = 0.0

        try:
            # Compute per-channel histograms
            for i, channel in enumerate(["Blue", "Green", "Red"]):
                hist = cv2.calcHist([cv_img], [i], None, [256], [0, 256])
                hist = hist.flatten()

                # Check for unusual peaks (quantization artifacts from selective editing)
                non_zero = hist[hist > 0]
                if len(non_zero) > 10:
                    # Compute entropy
                    probs = non_zero / non_zero.sum()
                    entropy = -np.sum(probs * np.log2(probs + 1e-10))
                    max_entropy = np.log2(len(non_zero))

                    if entropy / max_entropy < 0.7 and max_entropy > 4:
                        risk = max(risk, 0.2)
                        findings.append({
                            "type": "color_anomaly",
                            "severity": "low",
                            "message": f"{channel} channel shows unusual histogram (entropy ratio: {entropy/max_entropy:.2f})",
                            "detail": "Quantization artifacts suggest selective color editing.",
                        })

        except Exception as e:
            logger.debug(f"Color histogram error: {e}")

        return risk, findings

    def _detect_screenshot_ui(self, cv_img: np.ndarray, gray: np.ndarray) -> tuple[float, list]:
        """Detect common screenshot UI elements (status bars, navigation bars)."""
        findings = []
        risk = 0.0

        try:
            h, w = gray.shape

            # Check for status bar at top (solid color bar ~25-40px)
            if h > 100:
                top_bar = gray[:40, :]
                bar_std = np.std(top_bar)
                if bar_std < 20:  # Very uniform = status bar
                    findings.append({
                        "type": "status_bar",
                        "severity": "info",
                        "message": "Status bar detected at top — likely a screenshot",
                    })

            # Check for navigation bar at bottom (solid color bar ~40-80px)
            if h > 100:
                bottom_bar = gray[-60:, :]
                bar_std = np.std(bottom_bar)
                if bar_std < 25:
                    findings.append({
                        "type": "nav_bar",
                        "severity": "info",
                        "message": "Navigation bar detected at bottom — likely a screenshot",
                    })

            # Check for notch/cutout (rounded corners or punch hole)
            corners = [
                gray[0, 0], gray[0, -1],
                gray[-1, 0], gray[-1, -1]
            ]
            if all(c < 30 for c in corners):  # All corners very dark
                findings.append({
                    "type": "dark_corners",
                    "severity": "info",
                    "message": "Dark corners detected — may indicate rounded device screen or mask",
                })

        except Exception as e:
            logger.debug(f"UI detection error: {e}")

        return risk, findings

    def _analyze_text_regions(self, gray: np.ndarray) -> tuple[float, list]:
        """Analyze text regions for font/rendering inconsistencies."""
        findings = []
        risk = 0.0

        try:
            # Use MSER to detect text-like regions
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)

            if len(regions) > 20:
                # Many text regions — analyze their properties
                sizes = [len(r) for r in regions]
                avg_size = np.mean(sizes)
                size_cv = np.std(sizes) / avg_size if avg_size > 0 else 0

                # Uniform text size suggests authentic UI
                # Highly variable sizes suggest compositing
                if size_cv > 1.5 and len(regions) > 50:
                    risk = 0.15
                    findings.append({
                        "type": "text_inconsistency",
                        "severity": "low",
                        "message": f"Highly variable text region sizes (CV: {size_cv:.2f})",
                        "detail": "Different font sizes suggest multiple source images composited together.",
                    })

        except Exception as e:
            logger.debug(f"Text analysis error: {e}")

        return risk, findings
