"""投递多链接实体（REQ-ATT-003 高频主路径）。"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ApplicationLink(Base):
    __tablename__ = "application_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    # 链接名称（默认取域名或类型名）
    name: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(Text)
    # 类型：投递入口 / JD详情 / 笔试链接 / 公司官网 / 其他
    link_type: Mapped[str] = mapped_column(String(20), default="其他")
    # 失效标记
    is_invalid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
