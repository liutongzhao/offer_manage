"""沟通记录业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import COMMUNICATION_METHODS
from app.repositories import communication_repo
from app.schemas.communication import CommunicationCreate, CommunicationUpdate


def create_communication(
    db: Session, application_id: int, data: CommunicationCreate
):
    if data.method not in COMMUNICATION_METHODS:
        raise HTTPException(
            status_code=400, detail=f"沟通方式须为 {COMMUNICATION_METHODS}"
        )
    return communication_repo.create(db, data, application_id)


def get_or_404(db: Session, id: int):
    obj = communication_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="沟通记录不存在")
    return obj


def update_communication(db: Session, id: int, data: CommunicationUpdate):
    obj = get_or_404(db, id)
    if data.method is not None and data.method not in COMMUNICATION_METHODS:
        raise HTTPException(
            status_code=400, detail=f"沟通方式须为 {COMMUNICATION_METHODS}"
        )
    return communication_repo.update(db, obj, data)


def delete_communication(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    communication_repo.delete(db, obj)
