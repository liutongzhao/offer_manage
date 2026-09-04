"""附件实体（JD 截图 / 笔试 / offer / 聊天记录等，REQ-ATT-001）。

简历仍为独立实体（Q-5 决策：简历与附件分离），附件覆盖其余素材类型。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(String(512))
    size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # 类型：简历 / JD截图 / 笔试 / offer / 聊天记录 / 证明材料 / 其他
    att_type: Mapped[str] = mapped_column(String(20), default="其他")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
