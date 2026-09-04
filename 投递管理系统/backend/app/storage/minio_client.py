"""MinIO 客户端封装：上传 / 预签名 URL / 下载 / 删除。"""
from datetime import timedelta
from io import BytesIO

from minio import Minio

from app.core.config import settings

_client: Minio | None = None

BUCKET_NAME = settings.minio_bucket


def get_client() -> Minio:
    """返回单例客户端，并确保桶存在。"""
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_use_ssl,
        )
        if not _client.bucket_exists(settings.minio_bucket):
            _client.make_bucket(settings.minio_bucket)
    return _client


def upload_file(object_key: str, data: bytes, content_type: str | None = None) -> None:
    client = get_client()
    client.put_object(
        settings.minio_bucket,
        object_key,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def get_presigned_url(object_key: str, expires: int = 3600) -> str:
    """返回预签名访问地址。

    注意：minio SDK 7.x 的 expires 参数要求是 timedelta，不是秒数（int）。
    """
    client = get_client()
    return client.presigned_get_object(
        settings.minio_bucket,
        object_key,
        expires=timedelta(seconds=expires),
    )


def download_file(object_key: str) -> bytes:
    client = get_client()
    resp = client.get_object(settings.minio_bucket, object_key)
    try:
        return resp.read()
    finally:
        resp.close()
        resp.release_conn()


def delete_file(object_key: str) -> None:
    client = get_client()
    client.remove_object(settings.minio_bucket, object_key)


def list_objects(prefix: str = "") -> list:
    """列出指定前缀下的对象（备份列表用）。"""
    client = get_client()
    return list(client.list_objects(settings.minio_bucket, prefix=prefix, recursive=True))
