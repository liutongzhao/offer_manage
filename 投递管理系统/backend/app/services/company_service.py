"""公司业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import company_repo
from app.schemas.company import CompanyCreate, CompanyUpdate


def create_company(db: Session, data: CompanyCreate):
    if company_repo.get_by_name(db, data.name):
        raise HTTPException(status_code=400, detail="公司已存在")
    return company_repo.create(db, data)


def get_or_404(db: Session, id: int):
    obj = company_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="公司不存在")
    return obj


def list_companies(db: Session, skip: int = 0, limit: int = 100):
    return company_repo.list_all(db, skip, limit)


def update_company(db: Session, id: int, data: CompanyUpdate):
    obj = get_or_404(db, id)
    return company_repo.update(db, obj, data)


def delete_company(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    company_repo.delete(db, obj)
