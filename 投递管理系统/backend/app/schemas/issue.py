"""问题记录相关 schema。"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class IssueCreate(BaseModel):
    title: str
    category: str = "其他"
    related_application_id: int | None = None
    description: str | None = None
    solution: str | None = None
    tags: str | None = None
    recorded_date: date | None = None


class IssueUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    related_application_id: int | None = None
    description: str | None = None
    solution: str | None = None
    tags: str | None = None
    recorded_date: date | None = None


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    related_application_id: int | None = None
    description: str | None = None
    solution: str | None = None
    tags: str | None = None
    recorded_date: date | None = None
    created_at: datetime | None = None
