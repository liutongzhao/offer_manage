"""投递记录实体。"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.application_link import ApplicationLink  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
from app.models.base import Base
from app.models.communication import Communication  # noqa: F401
from app.models.status_event import StatusEvent  # noqa: F401
from app.models.tag import application_tag


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # 后端开发/测试开发/AI开发
    position: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="待投递", index=True)
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    apply_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    jd_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_id: Mapped[int | None] = mapped_column(
        ForeignKey("resumes.id"), nullable=True
    )
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    tailor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(60), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    # 面试轮次（一面/二面/三面/HR面…自由文本）
    interview_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # 出结果（offer/挂）的日期
    result_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 归档：不参与默认列表；软删除：deleted_at 非空即视为已删除
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", back_populates="applications")
    resume = relationship("Resume", foreign_keys="Application.resume_id")

    # 溯源与素材关联
    events = relationship(
        "StatusEvent",
        foreign_keys="StatusEvent.application_id",
        cascade="all, delete-orphan",
    )
    communications = relationship(
        "Communication",
        foreign_keys="Communication.application_id",
        cascade="all, delete-orphan",
    )
    links = relationship(
        "ApplicationLink",
        foreign_keys="ApplicationLink.application_id",
        cascade="all, delete-orphan",
    )
    attachments = relationship(
        "Attachment",
        foreign_keys="Attachment.application_id",
        cascade="all, delete-orphan",
    )
    tags = relationship(
        "Tag", secondary=application_tag, back_populates="applications"
    )

    @property
    def company_name(self) -> str | None:
        """公司名快照（供响应序列化）。"""
        return self.company.name if self.company else None

    @property
    def tag_names(self) -> list[str]:
        """标签名列表（供响应序列化）。"""
        return [t.name for t in self.tags]
