"""投递链接数据访问层。"""
from sqlalchemy.orm import Session

from app.models.application_link import ApplicationLink
from app.schemas.link import LinkCreate, LinkUpdate


def create(db: Session, data: LinkCreate, application_id: int) -> ApplicationLink:
    payload = data.model_dump()
    if not payload.get("name"):
        payload["name"] = payload["link_type"]  # 默认名称取类型
    obj = ApplicationLink(application_id=application_id, **payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> ApplicationLink | None:
    return db.get(ApplicationLink, id)


def list_by_application(
    db: Session, application_id: int
) -> list[ApplicationLink]:
    return (
        db.query(ApplicationLink)
        .filter(ApplicationLink.application_id == application_id)
        .order_by(ApplicationLink.id.asc())
        .all()
    )


def update(db: Session, obj: ApplicationLink, data: LinkUpdate) -> ApplicationLink:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: ApplicationLink) -> None:
    db.delete(obj)
    db.commit()
