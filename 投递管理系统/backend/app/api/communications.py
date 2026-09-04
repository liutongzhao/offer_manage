"""沟通记录路由层（挂在投递下创建，独立路由维护）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.repositories import application_repo
from app.schemas.common import ApiResponse
from app.schemas.communication import (
    CommunicationCreate,
    CommunicationOut,
    CommunicationUpdate,
)
from app.services import communication_service

router = APIRouter(prefix="/api/v1", tags=["沟通"])


def _check_application(db: Session, application_id: int) -> None:
    if not application_repo.get(db, application_id):
        raise HTTPException(status_code=404, detail="投递记录不存在")


@router.post(
    "/applications/{application_id}/communications",
    response_model=ApiResponse[CommunicationOut],
)
def create(
    application_id: int, data: CommunicationCreate, db: Session = Depends(get_db)
):
    _check_application(db, application_id)
    obj = communication_service.create_communication(db, application_id, data)
    return ApiResponse(data=CommunicationOut.model_validate(obj))


@router.get(
    "/applications/{application_id}/communications",
    response_model=ApiResponse[list[CommunicationOut]],
)
def list_by_application(
    application_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    from app.repositories import communication_repo

    items = communication_repo.list_by_application(
        db, application_id, skip, limit
    )
    return ApiResponse(data=[CommunicationOut.model_validate(i) for i in items])


@router.patch("/communications/{id}", response_model=ApiResponse[CommunicationOut])
def update(id: int, data: CommunicationUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=CommunicationOut.model_validate(
            communication_service.update_communication(db, id, data)
        )
    )


@router.delete("/communications/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    communication_service.delete_communication(db, id)
    return ApiResponse(data=None)
