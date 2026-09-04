"""公司相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    scale: str | None = None
    website: str | None = None
    notes: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    scale: str | None = None
    website: str | None = None
    notes: str | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    scale: str | None = None
    website: str | None = None
    notes: str | None = None
    created_at: datetime | None = None


class CompanyWithCount(CompanyOut):
    """公司列表项：附带投递数聚合（REQ-COM-002）。"""

    application_count: int = 0
