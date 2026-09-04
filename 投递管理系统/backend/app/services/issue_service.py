"""问题记录业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import issue_repo
from app.schemas.issue import IssueCreate, IssueUpdate


def create_issue(db: Session, data: IssueCreate):
    return issue_repo.create(db, data)


def get_or_404(db: Session, id: int):
    obj = issue_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="问题记录不存在")
    return obj


def list_issues(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    related_application_id: int | None = None,
):
    return issue_repo.list_all(
        db, skip, limit, category=category, related_application_id=related_application_id
    )


def update_issue(db: Session, id: int, data: IssueUpdate):
    obj = get_or_404(db, id)
    return issue_repo.update(db, obj, data)


def delete_issue(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    issue_repo.delete(db, obj)
