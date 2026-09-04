"""投递记录相关 schema。"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    company_id: int
    type: str = Field(..., description="后端开发/测试开发/AI开发")
    position: str
    status: str = "待投递"
    channel: str | None = None
    apply_date: date | None = None
    city: str | None = None
    jd_url: str | None = None
    resume_id: int | None = None
    requirements: str | None = None
    tailor_notes: str | None = None
    referrer: str | None = None
    salary: str | None = None
    deadline: date | None = None
    interview_stage: str | None = None
    result_date: date | None = None
    notes: str | None = None
    # 创建时可同时打标签（自由输入，自动建档）
    tag_names: list[str] | None = None


class ApplicationUpdate(BaseModel):
    type: str | None = None
    position: str | None = None
    status: str | None = None
    channel: str | None = None
    apply_date: date | None = None
    city: str | None = None
    jd_url: str | None = None
    resume_id: int | None = None
    requirements: str | None = None
    tailor_notes: str | None = None
    referrer: str | None = None
    salary: str | None = None
    deadline: date | None = None
    interview_stage: str | None = None
    result_date: date | None = None
    notes: str | None = None
    archived: bool | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    company_name: str | None = None
    type: str
    position: str
    status: str
    channel: str | None = None
    apply_date: date | None = None
    city: str | None = None
    jd_url: str | None = None
    resume_id: int | None = None
    requirements: str | None = None
    tailor_notes: str | None = None
    referrer: str | None = None
    salary: str | None = None
    deadline: date | None = None
    interview_stage: str | None = None
    result_date: date | None = None
    notes: str | None = None
    archived: bool = False
    tag_names: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApplicationListData(BaseModel):
    """列表分页数据。"""

    total: int
    items: list[ApplicationOut]
