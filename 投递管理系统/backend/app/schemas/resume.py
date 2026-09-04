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
