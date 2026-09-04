"""简历资产相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str | None = None
    application_id: int | None = None
    filename: str
    object_key: str
    size: int | None = None
    content_type: str | None = None
    is_base: bool = False
    version: str | None = None
    uploaded_at: datetime | None = None


class ResumeUpdate(BaseModel):
    """简历部分更新（用于事后关联投递 / 调整标注）。"""

    application_id: int | None = None
    company: str | None = None
    version: str | None = None
    is_base: bool | None = None
