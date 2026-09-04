"""统计分析相关 schema。"""
from datetime import date

from pydantic import BaseModel


class SummaryOut(BaseModel):
    total: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_channel: dict[str, int]
    issues_total: int
    week_count: int = 0
    interviewing: int = 0
    offered: int = 0
    conversion_rate: float = 0.0


class FunnelStage(BaseModel):
    stage: str
    count: int
    percent: float = 0.0


class FunnelOut(BaseModel):
    stages: list[FunnelStage]


class TrendPoint(BaseModel):
    period: str  # 如 2026-W36 / 2026-09
    count: int


class TodoItem(BaseModel):
    application_id: int
    company_name: str | None = None
    position: str
    status: str
    deadline: date
    days_left: int  # 负数表示已过期


class TodosOut(BaseModel):
    expired: list[TodoItem]
    due_soon: list[TodoItem]


class RecentEventItem(BaseModel):
    """看板近期动态条目。"""

    kind: str  # status / field / communication / attachment / issue
    time: str
    application_id: int
    company_name: str | None = None
    position: str | None = None
    summary: str
