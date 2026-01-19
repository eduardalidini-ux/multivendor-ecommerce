import mimetypes
import posixpath
from dataclasses import dataclass

import boto3
from botocore.config import Config
from django.conf import settings


@dataclass(frozen=True)
class PresignedUrl:
    url: str
    key: str


def _s3_client():
    return boto3.client(
        "s3",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
    )


def guess_content_type(filename_or_path: str) -> str:
    content_type, _ = mimetypes.guess_type(filename_or_path)
    return content_type or "application/octet-stream"


def normalize_key(key: str) -> str:
    # Ensure no leading slash and normalize separators to '/'
    key = key.replace("\\", "/").lstrip("/")
    return posixpath.normpath(key)


def presign_put(key: str, content_type: str | None = None, expires_in: int = 60 * 10) -> PresignedUrl:
    key = normalize_key(key)
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    client = _s3_client()

    params = {"Bucket": bucket, "Key": key}
    # IMPORTANT: Do not include ContentType in Params.
    # Browsers may send a slightly different Content-Type than what we guess,
    # which causes Supabase S3 to return SignatureDoesNotMatch.

    url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=expires_in,
        HttpMethod="PUT",
    )
    return PresignedUrl(url=url, key=key)


def presign_get(key: str, expires_in: int = 60 * 10) -> str:
    if not key:
        return ""
    key = normalize_key(key)
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    client = _s3_client()

    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
        HttpMethod="GET",
    )
