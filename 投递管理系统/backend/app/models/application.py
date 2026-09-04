"""投递记录实体。"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # 后端开发/测试开发/AI开发
    position: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="待投递")
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    apply_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    city: Mapped[str | None] = mapped_column(String(60), nullable=True)
    jd_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_id: Mapped[int | None] = mapped_column(
        ForeignKey("resumes.id"), nullable=True
    )
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    tailor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(60), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", back_populates="applications")
    resume = relationship("Resume", foreign_keys="Application.resume_id")
