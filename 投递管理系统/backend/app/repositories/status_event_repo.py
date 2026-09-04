"""状态事件数据访问层。"""
from sqlalchemy.orm import Session

from app.models.status_event import StatusEvent


def create(db: Session, **kwargs) -> StatusEvent:
    obj = StatusEvent(**kwargs)
    db.add(obj)
    return obj  # 由调用方统一 commit


def list_by_application(
    db: Session, application_id: int, skip: int = 0, limit: int = 100
) -> list[StatusEvent]:
    return (
        db.query(StatusEvent)
        .filter(StatusEvent.application_id == application_id)
        .order_by(StatusEvent.event_time.desc(), StatusEvent.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
