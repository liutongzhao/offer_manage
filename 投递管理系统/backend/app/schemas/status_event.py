"""状态事件（溯源）相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StatusEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    event_type: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    description: str | None = None
    source: str
    event_time: datetime | None = None


class TimelineItem(BaseModel):
    """统一时间线条目（状态事件 / 沟通记录 / 附件 / 简历 / 问题混排）。"""

    kind: str  # status / field / create / communication / attachment / resume / issue
    time: datetime
    id: int | None = None
    application_id: int | None = None
    # 事件类
    event_type: str | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    source: str | None = None
    # 沟通类
    contact: str | None = None
    method: str | None = None
    content: str | None = None
    my_action: str | None = None
    # 附件/简历类
    filename: str | None = None
    att_type: str | None = None
    # 问题类
    title: str | None = None
    # 通用摘要与展示
    description: str | None = None
