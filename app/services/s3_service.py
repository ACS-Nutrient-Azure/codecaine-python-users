import json
import logging
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

_s3_client = None


def _get_client():
    global _s3_client
    if _s3_client is None:
        kwargs = {"region_name": settings.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        _s3_client = boto3.client("s3", **kwargs)
    return _s3_client


def upload_json(cognito_id: str, filename: str, data: dict) -> str:
    key = f"health-data/{cognito_id}/{filename}"
    try:
        client = _get_client()
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=json.dumps(data, ensure_ascii=False, default=str),
            ContentType="application/json",
        )
        logger.info("[S3] 업로드 완료: s3://%s/%s", settings.s3_bucket_name, key)
        return key
    except Exception as e:
        logger.warning("[S3] 업로드 실패 (계속 진행): %s", str(e))
        return ""


def download_json(cognito_id: str, filename: str) -> dict | None:
    key = f"health-data/{cognito_id}/{filename}"
    try:
        client = _get_client()
        response = client.get_object(Bucket=settings.s3_bucket_name, Key=key)
        content = response["Body"].read().decode("utf-8")
        return json.loads(content)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logger.info("[S3] 파일 없음: %s", key)
        else:
            logger.warning("[S3] 다운로드 실패: %s", str(e))
        return None
    except Exception as e:
        logger.warning("[S3] 다운로드 실패: %s", str(e))
        return None
