"""分析路由层：汇总 / 漏斗 / 趋势 / 待办 / 近期动态。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.analytics import (
    FunnelOut,
    RecentEventItem,
    SummaryOut,
    TodosOut,
    TrendPoint,
)
from app.schemas.common import ApiResponse
from app.services import analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["分析"])


@router.get("/summary", response_model=ApiResponse[SummaryOut])
def summary(db: Session = Depends(get_db)):
    return ApiResponse(data=SummaryOut(**analytics_service.get_summary(db)))


@router.get("/funnel", response_model=ApiResponse[FunnelOut])
def funnel(db: Session = Depends(get_db)):
    return ApiResponse(data=FunnelOut(**analytics_service.get_funnel(db)))


@router.get("/trend", response_model=ApiResponse[list[TrendPoint]])
def trend(
    granularity: str = Query("week", description="week / month"),
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
):
    return ApiResponse(
        data=[
            TrendPoint(**p)
            for p in analytics_service.get_trend(db, granularity, months)
        ]
    )


@router.get("/todos", response_model=ApiResponse[TodosOut])
def todos(db: Session = Depends(get_db)):
    """基于 deadline 的临期待办（7 天内截止 / 已过期分组）。"""
    return ApiResponse(data=TodosOut(**analytics_service.get_todos(db)))


@router.get("/recent-events", response_model=ApiResponse[list[RecentEventItem]])
def recent_events(limit: int = Query(10, le=50), db: Session = Depends(get_db)):
    return ApiResponse(
        data=[RecentEventItem(**i) for i in analytics_service.get_recent_events(db, limit)]
    )
