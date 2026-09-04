"""附件相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    filename: str
    object_key: str
    size: int | None = None
    content_type: str | None = None
    att_type: str
    uploaded_at: datetime | None = None


class AttachmentUpdate(BaseModel):
    att_type: str | None = None
