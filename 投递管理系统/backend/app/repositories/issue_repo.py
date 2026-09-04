"""问题记录数据访问层。"""
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueUpdate


def create(db: Session, data: IssueCreate) -> Issue:
    obj = Issue(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Issue | None:
    return db.get(Issue, id)


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    related_application_id: int | None = None,
) -> list[Issue]:
    q = db.query(Issue)
    if category:
        q = q.filter(Issue.category == category)
    if related_application_id:
        q = q.filter(Issue.related_application_id == related_application_id)
    return q.order_by(Issue.id.desc()).offset(skip).limit(limit).all()


def update(db: Session, obj: Issue, data: IssueUpdate) -> Issue:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Issue) -> None:
    db.delete(obj)
    db.commit()
