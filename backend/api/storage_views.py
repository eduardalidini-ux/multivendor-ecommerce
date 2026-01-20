from __future__ import annotations

import uuid

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.storage_s3 import PresignedUrl, guess_content_type, presign_get, presign_put

from drf_spectacular.utils import extend_schema, inline_serializer

import boto3
from botocore.config import Config


def _require_storage_settings():
    missing = []
    for name in [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_STORAGE_BUCKET_NAME",
        "AWS_S3_ENDPOINT_URL",
        "AWS_S3_REGION_NAME",
    ]:
        if not getattr(settings, name, None):
            missing.append(name)
    return missing


class PresignUploadView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=inline_serializer(
            name="PresignUploadRequest",
            fields={},
        ),
        responses=inline_serializer(
            name="PresignUploadResponse",
            fields={},
        ),
    )
    def post(self, request):
        missing = _require_storage_settings()
        if missing:
            return Response(
                {"detail": "Missing storage env vars", "missing": missing},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        bucket = request.data.get("bucket")
        key_prefix = request.data.get("key_prefix", "")
        filename = request.data.get("filename")
        content_type = request.data.get("content_type")

        if not bucket or not filename:
            return Response(
                {"detail": "bucket and filename are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if bucket != settings.AWS_STORAGE_BUCKET_NAME:
            return Response(
                {"detail": "Invalid bucket"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = (filename.split(".")[-1] if "." in filename else "bin").lower()
        object_name = f"{uuid.uuid4()}.{ext}"
        key_prefix = (key_prefix or "").strip().strip("/")
        key = f"{key_prefix}/{object_name}" if key_prefix else object_name

        if not content_type:
            content_type = guess_content_type(filename)

        presigned: PresignedUrl = presign_put(key=key, content_type=None)
        return Response(
            {
                "upload_url": presigned.url,
                "key": presigned.key,
                "bucket": bucket,
                "content_type": content_type,
                "method": "PUT",
            },
            status=status.HTTP_200_OK,
        )


class PresignDownloadView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=inline_serializer(
            name="PresignDownloadRequest",
            fields={},
        ),
        responses=inline_serializer(
            name="PresignDownloadResponse",
            fields={},
        ),
    )
    def post(self, request):
        missing = _require_storage_settings()
        if missing:
            return Response(
                {"detail": "Missing storage env vars", "missing": missing},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        bucket = request.data.get("bucket")
        key = request.data.get("key")
        expires_in = request.data.get("expires_in", 60 * 10)

        if not bucket or not key:
            return Response(
                {"detail": "bucket and key are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if bucket != settings.AWS_STORAGE_BUCKET_NAME:
            return Response(
                {"detail": "Invalid bucket"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            expires_in = int(expires_in)
        except (TypeError, ValueError):
            expires_in = 60 * 10

        url = presign_get(key=key, expires_in=expires_in)
        return Response({"url": url}, status=status.HTTP_200_OK)


class DebugS3View(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        responses=inline_serializer(
            name="DebugS3Response",
            fields={},
        )
    )
    def get(self, request):
        missing = _require_storage_settings()
        if missing:
            return Response(
                {"detail": "Missing storage env vars", "missing": missing},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            client = boto3.client(
                "s3",
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
                region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
                endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
            )

            resp = client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, MaxKeys=5)
            keys = [obj.get("Key") for obj in resp.get("Contents", [])]
            return Response(
                {
                    "ok": True,
                    "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "endpoint": settings.AWS_S3_ENDPOINT_URL,
                    "region": settings.AWS_S3_REGION_NAME,
                    "sample_keys": keys,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "ok": False,
                    "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "endpoint": settings.AWS_S3_ENDPOINT_URL,
                    "region": settings.AWS_S3_REGION_NAME,
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                },
                status=status.HTTP_200_OK,
            )
