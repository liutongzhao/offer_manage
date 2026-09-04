"""投递多链接相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LinkCreate(BaseModel):
    url: str = Field(..., min_length=1)
    name: str | None = None
    link_type: str = "其他"

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("链接地址不能为空")
        return v


class LinkUpdate(BaseModel):
    url: str | None = None
    name: str | None = None
    link_type: str | None = None
    is_invalid: bool | None = None


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    name: str
    url: str
    link_type: str
    is_invalid: bool
    created_at: datetime | None = None
