"""投递多链接路由层。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.repositories import application_repo
from app.schemas.common import ApiResponse
from app.schemas.link import LinkCreate, LinkOut, LinkUpdate
from app.services import link_service

router = APIRouter(prefix="/api/v1", tags=["链接"])


def _check_application(db: Session, application_id: int) -> None:
    if not application_repo.get(db, application_id):
        raise HTTPException(status_code=404, detail="投递记录不存在")


@router.post(
    "/applications/{application_id}/links", response_model=ApiResponse[LinkOut]
)
def create(application_id: int, data: LinkCreate, db: Session = Depends(get_db)):
    _check_application(db, application_id)
    obj = link_service.create_link(db, application_id, data)
    return ApiResponse(data=LinkOut.model_validate(obj))


@router.get(
    "/applications/{application_id}/links",
    response_model=ApiResponse[list[LinkOut]],
)
def list_by_application(application_id: int, db: Session = Depends(get_db)):
    from app.repositories import link_repo

    return ApiResponse(
        data=[
            LinkOut.model_validate(i)
            for i in link_repo.list_by_application(db, application_id)
        ]
    )


@router.patch("/links/{id}", response_model=ApiResponse[LinkOut])
def update(id: int, data: LinkUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=LinkOut.model_validate(link_service.update_link(db, id, data))
    )


@router.delete("/links/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    link_service.delete_link(db, id)
    return ApiResponse(data=None)
