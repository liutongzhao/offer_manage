"""投递记录业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import APPLICATION_STATUSES, APPLICATION_TYPES
from app.repositories import application_repo, company_repo, resume_repo
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def _check_type_status(type_: str | None, status: str | None) -> None:
    if type_ is not None and type_ not in APPLICATION_TYPES:
        raise HTTPException(status_code=400, detail=f"类型须为 {APPLICATION_TYPES}")
    if status is not None and status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail=f"状态须为 {APPLICATION_STATUSES}")


def create_application(db: Session, data: ApplicationCreate):
    _check_type_status(data.type, data.status)
    if not company_repo.get(db, data.company_id):
        raise HTTPException(status_code=404, detail="关联公司不存在")
    if data.resume_id and not resume_repo.get(db, data.resume_id):
        raise HTTPException(status_code=404, detail="关联简历不存在")
    return application_repo.create(db, data)


def get_or_404(db: Session, id: int):
    obj = application_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return obj


def list_applications(db: Session, **filters):
    return application_repo.list_all(db, **filters)


def update_application(db: Session, id: int, data: ApplicationUpdate):
    obj = get_or_404(db, id)
    upd = data.model_dump(exclude_unset=True)
    _check_type_status(upd.get("type"), upd.get("status"))
    if "resume_id" in upd and upd["resume_id"] and not resume_repo.get(
        db, upd["resume_id"]
    ):
        raise HTTPException(status_code=404, detail="关联简历不存在")
    return application_repo.update(db, obj, data)


def delete_application(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    application_repo.delete(db, obj)
