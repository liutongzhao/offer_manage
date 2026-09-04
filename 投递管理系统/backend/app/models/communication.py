"""沟通记录实体（溯源核心，REQ-TRC-003）。"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Communication(Base):
    __tablename__ = "communications"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    # 沟通对象：HR / 面试官 / 内推人 / 其他
    contact: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # 沟通方式：微信 / 电话 / 邮件 / 现场 / 平台消息 / 其他
    method: Mapped[str] = mapped_column(String(20), default="其他")
    # 内容摘要
    content: Mapped[str] = mapped_column(Text)
    # 我方动作（可生成待办）
    my_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 沟通发生时间（支持自定义过去时间，Q-3 附带说明）
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
