"""数据导入导出相关 schema。"""
from pydantic import BaseModel


class ImportFailure(BaseModel):
    row: int
    error: str


class ImportResult(BaseModel):
    success_count: int
    fail_count: int
    failures: list[ImportFailure]


class BackupInfo(BaseModel):
    object_key: str
    size: int | None = None
    last_modified: str | None = None


class RestoreRequest(BaseModel):
    object_key: str
