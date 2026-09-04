"""投递记录数据访问层（含多维筛选）。"""
from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def create(db: Session, data: ApplicationCreate) -> Application:
    obj = Application(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Application | None:
    return db.get(Application, id)


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: str | None = None,
    status: str | None = None,
    city: str | None = None,
    company_id: int | None = None,
    channel: str | None = None,
) -> list[Application]:
    q = db.query(Application)
    if type:
        q = q.filter(Application.type == type)
    if status:
        q = q.filter(Application.status == status)
    if city:
        q = q.filter(Application.city == city)
    if company_id:
        q = q.filter(Application.company_id == company_id)
    if channel:
        q = q.filter(Application.channel == channel)
    return q.order_by(Application.id.desc()).offset(skip).limit(limit).all()


def update(db: Session, obj: Application, data: ApplicationUpdate) -> Application:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Application) -> None:
    db.delete(obj)
    db.commit()
