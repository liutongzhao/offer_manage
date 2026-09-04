"""投递记录路由层（含多维筛选）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.schemas.common import ApiResponse
from app.services import application_service

router = APIRouter(prefix="/api/v1/applications", tags=["投递"])


@router.post("", response_model=ApiResponse[ApplicationOut])
def create(data: ApplicationCreate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=ApplicationOut.model_validate(application_service.create_application(db, data))
    )


@router.get("", response_model=ApiResponse[list[ApplicationOut]])
def list_all(
    type: str | None = None,
    status: str | None = None,
    city: str | None = None,
    company_id: int | None = None,
    channel: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items = application_service.list_applications(
        db,
        type=type,
        status=status,
        city=city,
        company_id=company_id,
        channel=channel,
        skip=skip,
        limit=limit,
    )
    return ApiResponse(data=[ApplicationOut.model_validate(i) for i in items])


@router.get("/{id}", response_model=ApiResponse[ApplicationOut])
def get_one(id: int, db: Session = Depends(get_db)):
    return ApiResponse(
        data=ApplicationOut.model_validate(application_service.get_or_404(db, id))
    )


@router.patch("/{id}", response_model=ApiResponse[ApplicationOut])
def update(id: int, data: ApplicationUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=ApplicationOut.model_validate(
            application_service.update_application(db, id, data)
        )
    )


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    application_service.delete_application(db, id)
    return ApiResponse(data=None)
