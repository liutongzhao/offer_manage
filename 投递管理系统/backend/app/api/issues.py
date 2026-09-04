"""问题记录路由层。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.issue import IssueCreate, IssueOut, IssueUpdate
from app.services import issue_service

router = APIRouter(prefix="/api/v1/issues", tags=["问题"])


@router.post("", response_model=ApiResponse[IssueOut])
def create(data: IssueCreate, db: Session = Depends(get_db)):
    return ApiResponse(data=IssueOut.model_validate(issue_service.create_issue(db, data)))


@router.get("", response_model=ApiResponse[list[IssueOut]])
def list_all(
    category: str | None = None,
    related_application_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = issue_service.list_issues(
        db, skip, limit, category=category, related_application_id=related_application_id
    )
    return ApiResponse(data=[IssueOut.model_validate(i) for i in items])


@router.get("/{id}", response_model=ApiResponse[IssueOut])
def get_one(id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=IssueOut.model_validate(issue_service.get_or_404(db, id)))


@router.patch("/{id}", response_model=ApiResponse[IssueOut])
def update(id: int, data: IssueUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=IssueOut.model_validate(issue_service.update_issue(db, id, data))
    )


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    issue_service.delete_issue(db, id)
    return ApiResponse(data=None)
