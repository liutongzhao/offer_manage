"""标签数据访问层。"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.tag import Tag, application_tag


def create(db: Session, name: str, scope: str = "投递", color: str | None = None) -> Tag:
    obj = Tag(name=name, scope=scope, color=color)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Tag | None:
    return db.get(Tag, id)


def get_by_name(db: Session, name: str) -> Tag | None:
    return db.query(Tag).filter(Tag.name == name).first()


def list_all(db: Session, skip: int = 0, limit: int = 200) -> list[Tag]:
    return db.query(Tag).order_by(Tag.id.asc()).offset(skip).limit(limit).all()


def usage_counts(db: Session) -> dict[int, int]:
    rows = (
        db.query(application_tag.c.tag_id, func.count())
        .group_by(application_tag.c.tag_id)
        .all()
    )
    return {tag_id: cnt for tag_id, cnt in rows}


def update(db: Session, obj: Tag, name: str | None, color: str | None) -> Tag:
    if name is not None:
        obj.name = name
    if color is not None:
        obj.color = color
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Tag) -> None:
    db.delete(obj)  # 多对多关联行自动级联删除
    db.commit()
