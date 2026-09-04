"""投递记录路由层（多条件筛选 / 时间线 / 标签 / 软删除恢复）。"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListData,
    ApplicationOut,
    ApplicationUpdate,
)
from app.schemas.common import ApiResponse
from app.schemas.status_event import TimelineItem
from app.schemas.tag import ApplicationTagsSet
from app.services import application_service

router = APIRouter(prefix="/api/v1/applications", tags=["投递"])


@router.post("", response_model=ApiResponse[ApplicationOut])
def create(
    data: ApplicationCreate,
    source: str = Query("用户操作", description="操作来源：代理录入/用户操作/系统自动"),
    db: Session = Depends(get_db),
):
    obj = application_service.create_application(db, data, source=source)
    return ApiResponse(data=ApplicationOut.model_validate(obj))


@router.get("", response_model=ApiResponse[ApplicationListData])
def list_all(
    type: str | None = None,
    status: str | None = Query(None, description="支持逗号分隔多状态"),
    channel: str | None = None,
    city: str | None = None,
    company_id: int | None = None,
    referrer: str | None = None,
    keyword: str | None = Query(None, description="关键词：公司/岗位/备注/招聘要求"),
    tag: str | None = None,
    apply_date_from: date | None = None,
    apply_date_to: date | None = None,
    deadline_from: date | None = None,
    deadline_to: date | None = None,
    archived: bool = Query(False, description="true 查看已归档"),
    include_deleted: bool = Query(False, description="true 查看回收站"),
    sort_by: str = Query("id", description="id/apply_date/deadline/created_at/updated_at/status"),
    order: str = Query("desc", description="asc/desc"),
    skip: int = 0,
    limit: int = Query(20, le=200),
    db: Session = Depends(get_db),
):
    total, items = application_service.list_applications(
        db,
        skip=skip,
        limit=limit,
        type=type,
        status=status,
        channel=channel,
        city=city,
        company_id=company_id,
        referrer=referrer,
        keyword=keyword,
        tag=tag,
        apply_date_from=apply_date_from,
        apply_date_to=apply_date_to,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        archived=archived,
        include_deleted=include_deleted,
        sort_by=sort_by,
        order=order,
    )
    return ApiResponse(
        data=ApplicationListData(
            total=total,
            items=[ApplicationOut.model_validate(i) for i in items],
        )
    )


@router.get("/cities", response_model=ApiResponse[list[str]])
def cities(db: Session = Depends(get_db)):
    """筛选项：出现过的城市列表。"""
    from app.repositories import application_repo

    return ApiResponse(data=application_repo.distinct_cities(db))


@router.get("/{id}", response_model=ApiResponse[ApplicationOut])
def get_one(id: int, db: Session = Depends(get_db)):
    return ApiResponse(
        data=ApplicationOut.model_validate(application_service.get_or_404(db, id))
    )


@router.get("/{id}/timeline", response_model=ApiResponse[list[TimelineItem]])
def timeline(
    id: int,
    kind: str | None = Query(
        None, description="过滤：status/field/communication/attachment/issue"
    ),
    offset: int = 0,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """统一时间线（REQ-TRC-004）：状态事件+沟通+附件+简历+问题混排。"""
    application_service.get_or_404(db, id)
    items = application_service.build_timeline(db, id, kind, offset, limit)
    return ApiResponse(data=[TimelineItem(**i) for i in items])


@router.patch("/{id}", response_model=ApiResponse[ApplicationOut])
def update(
    id: int,
    data: ApplicationUpdate,
    source: str = Query("用户操作", description="操作来源：代理录入/用户操作/系统自动"),
    db: Session = Depends(get_db),
):
    obj = application_service.update_application(db, id, data, source=source)
    return ApiResponse(data=ApplicationOut.model_validate(obj))


@router.put("/{id}/tags", response_model=ApiResponse[ApplicationOut])
def set_tags(id: int, data: ApplicationTagsSet, db: Session = Depends(get_db)):
    """整体替换投递标签（自由输入，自动建档）。"""
    obj = application_service.set_application_tags(db, id, data.names)
    return ApiResponse(data=ApplicationOut.model_validate(obj))


@router.post("/{id}/restore", response_model=ApiResponse[ApplicationOut])
def restore(id: int, db: Session = Depends(get_db)):
    """从回收站恢复软删除的投递。"""
    obj = application_service.restore_application(db, id)
    return ApiResponse(data=ApplicationOut.model_validate(obj))


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    """软删除：置 deleted_at，可通过 /restore 恢复。"""
    application_service.delete_application(db, id)
    return ApiResponse(data=None)
