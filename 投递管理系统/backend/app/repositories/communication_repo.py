"""沟通记录数据访问层。"""
from sqlalchemy.orm import Session

from app.models.communication import Communication
from app.schemas.communication import CommunicationCreate, CommunicationUpdate


def create(db: Session, data: CommunicationCreate, application_id: int) -> Communication:
    payload = data.model_dump()
    if payload.get("occurred_at") is None:
        payload.pop("occurred_at")  # 让 server_default 生效
    obj = Communication(application_id=application_id, **payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Communication | None:
    return db.get(Communication, id)


def list_by_application(
    db: Session, application_id: int, skip: int = 0, limit: int = 100
) -> list[Communication]:
    return (
        db.query(Communication)
        .filter(Communication.application_id == application_id)
        .order_by(Communication.occurred_at.desc(), Communication.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update(db: Session, obj: Communication, data: CommunicationUpdate) -> Communication:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Communication) -> None:
    db.delete(obj)
    db.commit()
