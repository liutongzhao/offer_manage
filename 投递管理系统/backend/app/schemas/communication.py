"""沟通记录相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommunicationCreate(BaseModel):
    content: str
    contact: str | None = None
    method: str = "其他"
    my_action: str | None = None
    # 沟通发生时间，支持自定义过去时间；不传则取当前时间
    occurred_at: datetime | None = Field(default=None)


class CommunicationUpdate(BaseModel):
    content: str | None = None
    contact: str | None = None
    method: str | None = None
    my_action: str | None = None
    occurred_at: datetime | None = None


class CommunicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    contact: str | None = None
    method: str
    content: str
    my_action: str | None = None
    occurred_at: datetime | None = None
    created_at: datetime | None = None
