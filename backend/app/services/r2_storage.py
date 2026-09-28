import io
import json
from typing import Any, BinaryIO, Optional

import boto3
from botocore.client import Config

from app.config import settings


class R2StorageService:
    """Cloudflare R2/S3-compatible object storage. Credentials stay backend-only."""

    def __init__(self):
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(
            getattr(settings, "R2_ENABLED", False)
            and getattr(settings, "R2_ENDPOINT_URL", "")
            and getattr(settings, "R2_ACCESS_KEY_ID", "")
            and getattr(settings, "R2_SECRET_ACCESS_KEY", "")
            and getattr(settings, "R2_BUCKET_NAME", "")
        )

    def _require(self):
        if not self.enabled:
            raise RuntimeError("R2 storage is not configured")

    @property
    def client(self):
        self._require()
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name=settings.R2_REGION or "auto",
                config=Config(signature_version="s3v4"),
            )
        return self._client

    @property
    def bucket(self):
        self._require()
        return settings.R2_BUCKET_NAME

    def upload_fileobj(self, fileobj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
        extra = {"ContentType": content_type} if content_type else {}
        self.client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra)
        return key

    def upload_bytes(self, data: bytes, key: str, content_type: Optional[str] = None) -> str:
        return self.upload_fileobj(io.BytesIO(data), key, content_type)

    def upload_json(self, value: Any, key: str) -> str:
        return self.upload_bytes(
            json.dumps(value, ensure_ascii=False, default=str).encode("utf-8"),
            key,
            "application/json",
        )

    def download_bytes(self, key: str) -> bytes:
        out = io.BytesIO()
        self.client.download_fileobj(self.bucket, key, out)
        return out.getvalue()

    def download_json(self, key: str) -> Any:
        return json.loads(self.download_bytes(key).decode("utf-8"))

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def signed_url(self, key: str, expires_seconds: Optional[int] = None, response_content_type: Optional[str] = None) -> str:
        params = {"Bucket": self.bucket, "Key": key}
        if response_content_type:
            params["ResponseContentType"] = response_content_type
        return self.client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires_seconds or settings.R2_SIGNED_URL_EXPIRE_SECONDS,
        )


r2_storage = R2StorageService()
