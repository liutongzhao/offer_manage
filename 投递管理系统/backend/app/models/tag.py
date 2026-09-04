"""标签实体与投递-标签多对多关联（REQ-TAG-001）。"""
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# 投递-标签 多对多
application_tag = Table(
    "application_tags",
    Base.metadata,
    Column("application_id", ForeignKey("applications.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    # 适用对象：投递 / 问题 / 公司
    scope: Mapped[str] = mapped_column(String(20), default="投递")
    # 可视化颜色（可为空，前端给默认色）
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    applications = relationship(
        "Application", secondary=application_tag, back_populates="tags"
    )
