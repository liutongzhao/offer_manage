"""状态事件实体（溯源核心，REQ-TRC-001/005）。"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StatusEvent(Base):
    __tablename__ = "status_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    # 事件类型：状态变更 / 字段变更 / 创建记录
    event_type: Mapped[str] = mapped_column(String(20), default="字段变更")
    # 变更字段的中文展示名（状态变更时也填「当前状态」）
    field_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 操作来源：代理录入 / 用户操作 / 系统自动
    source: Mapped[str] = mapped_column(String(20), default="用户操作")
    # 事件时间（支持补录语义，创建时取当前时间）
    event_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
