from __future__ import annotations

from typing import Iterable

from botocore.exceptions import ClientError


def delete_field_file(
    instance,
    field_name: str,
    skip_names: set[str] | None = None,
    required_prefixes: set[str] | None = None,
) -> None:
    f = getattr(instance, field_name, None)
    if not f:
        return

    name = getattr(f, "name", "") or ""
    if not name:
        return

    if skip_names and name in skip_names:
        return

    if required_prefixes and not any(name.startswith(p) for p in required_prefixes):
        return

    try:
        f.delete(save=False)
    except ClientError as e:
        code = (
            e.response.get("Error", {}).get("Code")
            if getattr(e, "response", None)
            else None
        )
        if code in {"NoSuchKey", "404", "NotFound"}:
            return
        raise


def _s3_client_from_settings():
    import boto3
    from botocore.config import Config
    from django.conf import settings

    return boto3.client(
        "s3",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
    )


def _iter_s3_keys(bucket: str, prefix: str) -> Iterable[str]:
    from django.conf import settings

    if not getattr(settings, "USE_S3_MEDIA", False):
        return

    client = _s3_client_from_settings()
    continuation_token = None

    while True:
        params = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if continuation_token:
            params["ContinuationToken"] = continuation_token

        resp = client.list_objects_v2(**params)
        for obj in resp.get("Contents", []) or []:
            key = obj.get("Key")
            if key:
                yield key

        if resp.get("IsTruncated"):
            continuation_token = resp.get("NextContinuationToken")
            continue
        break


def delete_s3_prefix(prefix: str) -> int:
    """Delete all objects in the configured bucket under the given prefix.

    Returns number of objects deleted (best-effort).
    """
    from django.conf import settings

    if not getattr(settings, "USE_S3_MEDIA", False):
        return 0

    bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
    if not bucket:
        return 0

    normalized = (prefix or "").lstrip("/")
    if normalized and not normalized.endswith("/"):
        normalized += "/"

    client = _s3_client_from_settings()
    deleted = 0
    batch: list[dict[str, str]] = []

    for key in _iter_s3_keys(bucket=bucket, prefix=normalized):
        batch.append({"Key": key})
        if len(batch) >= 1000:
            resp = client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
            deleted += len(resp.get("Deleted", []) or batch)
            batch = []

    if batch:
        resp = client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
        deleted += len(resp.get("Deleted", []) or batch)

    return deleted


def user_prefix(user_id: int | str) -> str:
    return f"user_{user_id}/"
