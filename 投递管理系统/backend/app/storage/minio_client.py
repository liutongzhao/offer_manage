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


def _split_endpoint(endpoint: str) -> tuple[str, bool]:
    """拆出 (host[:port], 是否 ssl)。支持 http:// / https:// 前缀；无前缀沿用 minio_use_ssl。"""
    if endpoint.startswith("https://"):
        return endpoint[len("https://"):], True
    if endpoint.startswith("http://"):
        return endpoint[len("http://"):], False
    return endpoint, settings.minio_use_ssl


def get_presign_client() -> Minio:
    """生成预签名 URL 用的客户端。

    服务器部署时 minio_endpoint 指向容器内网地址（如 host.docker.internal:9000），
    浏览器拿到的 URL 必须是可达的外网地址，故预签名单独用外部端点。
    外部端点支持 https:// 前缀（走域名 HTTPS 时必须）。
    未配置外部端点时与内部端点一致（本地开发场景，行为不变）。
    """
    external = settings.minio_external_endpoint or settings.minio_endpoint
    if external == settings.minio_endpoint:
        return get_client()
    host, secure = _split_endpoint(external)
    return Minio(
        host,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=secure,
    )


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
    client = get_presign_client()
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
