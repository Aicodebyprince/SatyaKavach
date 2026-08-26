"""
SatyaKavach - AWS S3 / MinIO Storage Service
Handles evidence storage, signed URLs, file management
"""

import hashlib
import os
from typing import Optional
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class StorageService:
    """S3-compatible storage for evidence artifacts.

    Falls back to local-disk storage (./local_storage/) whenever S3/MinIO is
    unreachable — keeps local development and demos fully functional.
    """

    LOCAL_DIR = os.path.join(os.getcwd(), "local_storage")

    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    async def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.s3.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={"LocationConstraint": settings.S3_REGION}
                if settings.S3_REGION != "us-east-1"
                else {},
            )

    def _put(self, key: str, data: bytes, content_type: str) -> str:
        """Upload to S3; fall back to local disk if S3 is unavailable."""
        try:
            self.s3.put_object(
                Bucket=self.bucket, Key=key, Body=data, ContentType=content_type,
            )
            return key
        except Exception as exc:  # noqa: BLE001 — any S3 failure → local mode
            path = os.path.join(self.LOCAL_DIR, key)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            return f"local:{key}"

    def upload_file(self, file_data: bytes, media_id: str, filename: str) -> str:
        """Upload file to S3 and return the object key."""
        ext = os.path.splitext(filename)[1]
        key = f"uploads/{media_id}/original{ext}"
        return self._put(key, file_data, self._guess_mime(filename))

    def upload_artifact(self, media_id: str, artifact_path: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload an artifact (face crop, frame, spectrogram, etc.)."""
        key = f"artifacts/{media_id}/{artifact_path}"
        return self._put(key, data, content_type)

    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed URL for secure file access."""
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, key: str):
        """Delete a file from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except ClientError:
            pass

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """Compute SHA-256 hash for deduplication."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _guess_mime(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".webp": "image/webp", ".mp4": "video/mp4", ".mov": "video/quicktime",
            ".avi": "video/x-msvideo", ".mp3": "audio/mpeg", ".wav": "audio/wav",
            ".m4a": "audio/x-m4a",
        }
        return mime_map.get(ext, "application/octet-stream")


# Singleton instance
storage = StorageService()
