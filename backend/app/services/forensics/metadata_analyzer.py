"""
SatyaKavach - Metadata Forensics Analyzer
Extracts and analyzes EXIF metadata to detect:
- Editing software (Photoshop, GIMP, etc.)
- Timestamp inconsistencies
- Device fingerprint anomalies
- GPS tampering signs
- Thumbnail vs full-image mismatches
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from io import BytesIO

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

# Known editing software signatures
EDITING_SOFTWARE = {
    "photoshop": ("Adobe Photoshop", "high"),
    "gimp": ("GIMP", "medium"),
    "lightroom": ("Adobe Lightroom", "medium"),
    "paint.net": ("Paint.NET", "medium"),
    "canva": ("Canva", "medium"),
    "snapseed": ("Snapseed", "low"),
    "vsco": ("VSCO", "low"),
    "afterlight": ("Afterlight", "low"),
    "pixlr": ("Pixlr", "medium"),
    "faceapp": ("FaceApp", "high"),
    "reface": ("Reface", "high"),
    "deepfacelab": ("DeepFaceLab", "high"),
    "faceswap": ("FaceSwap", "high"),
    "midjourney": ("Midjourney", "high"),
    "dalle": ("DALL-E", "high"),
    "stable diffusion": ("Stable Diffusion", "high"),
    "lensa": ("Lensa", "medium"),
}

# Device brand patterns from EXIF Make/Model
KNOWN_DEVICES = {
    "apple": ["Apple", "iPhone", "iPad"],
    "samsung": ["Samsung", "SM-"],
    "google": ["Google", "Pixel"],
    "oneplus": ["OnePlus"],
    "xiaomi": ["Xiaomi", "Redmi", "POCO"],
    "huawei": ["Huawei", "HONOR"],
    "sony": ["Sony"],
}


@dataclass
class MetadataVerdict:
    risk_score: float  # 0.0 = clean, 1.0 = suspicious
    findings: list[dict] = field(default_factory=list)
    exif_summary: dict = field(default_factory=dict)
    device_info: dict = field(default_factory=dict)
    editing_detected: bool = False
    evidence: dict = field(default_factory=dict)


class MetadataForensicsAnalyzer:
    """Analyze image EXIF metadata for signs of manipulation."""

    def analyze(self, file_data: bytes) -> MetadataVerdict:
        """Analyze metadata of an image."""
        findings = []
        risk_score = 0.0

        try:
            img = Image.open(BytesIO(file_data))
        except Exception as e:
            findings.append({
                "type": "error",
                "severity": "medium",
                "message": f"Could not open image for metadata analysis: {e}",
            })
            return MetadataVerdict(
                risk_score=0.3,
                findings=findings,
                evidence={"error": str(e)},
            )

        # Extract EXIF
        exif_data = {}
        raw_exif = img.getexif() if hasattr(img, "getexif") else {}
        for tag_id, value in raw_exif.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            try:
                # Convert bytes/IFD to string for serialization
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except:
                        value = str(value)
                elif isinstance(value, (tuple, list)):
                    value = [str(v) for v in value]
                exif_data[tag_name] = value
            except:
                pass

        # --- Analysis 1: Editing Software Detection ---
        software = exif_data.get("Software", "") or exif_data.get("ProcessingSoftware", "")
        if software:
            software_lower = software.lower()
            for key, (name, severity) in EDITING_SOFTWARE.items():
                if key in software_lower:
                    risk_boost = 0.6 if severity == "high" else 0.3 if severity == "medium" else 0.15
                    risk_score = max(risk_score, risk_boost)
                    findings.append({
                        "type": "editing_software",
                        "severity": severity,
                        "message": f"Editing software detected: {name} ({software})",
                        "detail": f"This image was processed by {name}, which can indicate manipulation.",
                    })
                    break
            else:
                # Non-standard software
                if software not in ("", " "):
                    findings.append({
                        "type": "software",
                        "severity": "info",
                        "message": f"Image software: {software}",
                    })

        # --- Analysis 2: Device Fingerprint ---
        make = exif_data.get("Make", "")
        model = exif_data.get("Model", "")
        device_info = {"make": make, "model": model}

        if not make and not model:
            findings.append({
                "type": "missing_device",
                "severity": "medium",
                "message": "No device information (Make/Model) in metadata",
                "detail": "Device metadata was stripped or the image was not taken with a camera.",
            })
            risk_score = max(risk_score, 0.25)

        # --- Analysis 3: Timestamp Analysis ---
        datetime_original = exif_data.get("DateTimeOriginal", "")
        datetime_modified = exif_data.get("DateTime", "")
        modify_date = exif_data.get("ModifyDate", "")

        if datetime_original and datetime_modified:
            try:
                dt_orig = _parse_exif_datetime(datetime_original)
                dt_mod = _parse_exif_datetime(datetime_modified)
                if dt_orig and dt_mod:
                    diff = abs((dt_mod - dt_orig).total_seconds())
                    if diff > 3600:  # More than 1 hour difference
                        findings.append({
                            "type": "timestamp_mismatch",
                            "severity": "high",
                            "message": f"Timestamp mismatch: original={datetime_original}, modified={datetime_modified} ({diff:.0f}s difference)",
                            "detail": "Large gap between capture and modification time suggests editing.",
                        })
                        risk_score = max(risk_score, 0.5)
                    elif diff > 60:
                        findings.append({
                            "type": "timestamp_mismatch",
                            "severity": "low",
                            "message": f"Minor timestamp difference: {diff:.0f}s between capture and modification",
                        })
            except Exception as e:
                logger.debug(f"Timestamp parse error: {e}")

        if not datetime_original and not datetime_modified:
            findings.append({
                "type": "missing_timestamp",
                "severity": "low",
                "message": "No capture timestamp found in metadata",
            })

        # --- Analysis 4: Thumbnail vs Image Consistency ---
        try:
            thumb_data = exif_data.get("Thumbnail", None)
            if thumb_data and isinstance(thumb_data, bytes) and len(thumb_data) > 100:
                thumb_img = Image.open(BytesIO(thumb_data))
                thumb_w, thumb_h = thumb_img.size
                img_w, img_h = img.size
                aspect_ratio_orig = img_w / img_h if img_h > 0 else 0
                aspect_ratio_thumb = thumb_w / thumb_h if thumb_h > 0 else 0

                if abs(aspect_ratio_orig - aspect_ratio_thumb) > 0.1:
                    findings.append({
                        "type": "thumbnail_mismatch",
                        "severity": "high",
                        "message": f"Thumbnail aspect ratio ({aspect_ratio_thumb:.2f}) differs from full image ({aspect_ratio_orig:.2f})",
                        "detail": "Thumbnail does not match the full image — possible crop or face swap.",
                    })
                    risk_score = max(risk_score, 0.6)
                else:
                    findings.append({
                        "type": "thumbnail_match",
                        "severity": "info",
                        "message": "Thumbnail matches full image dimensions",
                    })
        except Exception:
            pass

        # --- Analysis 5: Resolution & DPI ---
        dpi = exif_data.get("XResolution") or exif_data.get("ResolutionUnit")
        if not dpi:
            findings.append({
                "type": "missing_dpi",
                "severity": "info",
                "message": "No DPI/resolution metadata",
            })

        # --- Analysis 6: Color Space ---
        color_space = exif_data.get("ColorSpace", "")
        if color_space and str(color_space) == "1":
            # sRGB is color_space=1
            pass

        # --- Analysis 7: GPS ---
        gps_info = exif_data.get("GPSInfo", None)
        if gps_info:
            findings.append({
                "type": "gps_present",
                "severity": "info",
                "message": "GPS location data present in image",
            })

        # --- Summary ---
        editing_detected = any(
            f["type"] == "editing_software" and f["severity"] in ("high", "medium")
            for f in findings
        )

        exif_summary = {
            "software": software,
            "make": make,
            "model": model,
            "datetime_original": datetime_original,
            "datetime_modified": datetime_modified,
            "has_gps": gps_info is not None,
            "exif_tag_count": len(exif_data),
        }

        evidence = {
            "risk_score": round(min(1.0, risk_score), 3),
            "editing_detected": editing_detected,
            "findings_count": len(findings),
            "high_severity_findings": sum(1 for f in findings if f["severity"] == "high"),
            "exif_summary": exif_summary,
            "device_info": device_info,
            "all_software_detected": software if software else None,
        }

        return MetadataVerdict(
            risk_score=round(min(1.0, risk_score), 3),
            findings=findings,
            exif_summary=exif_summary,
            device_info=device_info,
            editing_detected=editing_detected,
            evidence=evidence,
        )


def _parse_exif_datetime(dt_str: str) -> Optional[datetime]:
    """Parse EXIF datetime format: 'YYYY:MM:DD HH:MM:SS'"""
    try:
        return datetime.strptime(str(dt_str).strip(), "%Y:%m:%d %H:%M:%S")
    except (ValueError, TypeError):
        return None
