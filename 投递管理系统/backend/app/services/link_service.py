"""投递链接业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import LINK_TYPES
from app.repositories import link_repo
from app.schemas.link import LinkCreate, LinkUpdate


def create_link(db: Session, application_id: int, data: LinkCreate):
    if data.link_type not in LINK_TYPES:
        raise HTTPException(status_code=400, detail=f"链接类型须为 {LINK_TYPES}")
    return link_repo.create(db, data, application_id)


def get_or_404(db: Session, id: int):
    obj = link_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="链接不存在")
    return obj


def update_link(db: Session, id: int, data: LinkUpdate):
    obj = get_or_404(db, id)
    if data.link_type is not None and data.link_type not in LINK_TYPES:
        raise HTTPException(status_code=400, detail=f"链接类型须为 {LINK_TYPES}")
    return link_repo.update(db, obj, data)


def delete_link(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    link_repo.delete(db, obj)
