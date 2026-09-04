"""配置层：从 .env 读取运行参数（pydantic-settings）。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_root_user: str = "offer_admin"
    minio_root_password: str = "offer_password_123"
    minio_bucket: str = "qiuzhao"
    minio_use_ssl: bool = False

    # 数据库
    sqlite_path: str = "./data/app.db"

    # 跨域
    cors_origins: str = "http://localhost:5173"


settings = Settings()
