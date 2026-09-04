"""分析路由层：聚合统计。"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.application import Application
from app.models.issue import Issue
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["分析"])


@router.get("/summary", response_model=ApiResponse[dict])
def summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Application.id)).scalar() or 0
    by_type = dict(
        db.query(Application.type, func.count(Application.id))
        .group_by(Application.type)
        .all()
    )
    by_status = dict(
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    issues_total = db.query(func.count(Issue.id)).scalar() or 0
    return ApiResponse(
        data={
            "total": total,
            "by_type": by_type,
            "by_status": by_status,
            "issues_total": issues_total,
        }
    )
