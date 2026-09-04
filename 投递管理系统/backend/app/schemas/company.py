"""公司相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    website: str | None = None


class CompanyUpdate(BaseModel):
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    website: str | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    alias: str | None = None
    city: str | None = None
    industry: str | None = None
    website: str | None = None
    created_at: datetime | None = None
