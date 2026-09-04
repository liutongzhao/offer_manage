"""公司业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import application_repo, company_repo
from app.schemas.company import CompanyCreate, CompanyUpdate


def create_company(db: Session, data: CompanyCreate):
    if company_repo.get_by_name(db, data.name):
        raise HTTPException(status_code=400, detail=f"已存在同名公司「{data.name}」")
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
    upd = data.model_dump(exclude_unset=True)
    if "name" in upd and upd["name"] and upd["name"] != obj.name:
        existed = company_repo.get_by_name(db, upd["name"])
        if existed:
            raise HTTPException(status_code=400, detail=f"已存在同名公司「{upd['name']}」")
    return company_repo.update(db, obj, data)


def delete_company(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    company_repo.delete(db, obj)


def list_with_count(db: Session, skip: int = 0, limit: int = 100):
    """公司列表 + 每家投递数聚合（REQ-COM-002）。"""
    companies = company_repo.list_all(db, skip, limit)
    counts = application_repo.count_by_company(db)
    result = []
    for c in companies:
        item = {
            "id": c.id,
            "name": c.name,
            "alias": c.alias,
            "city": c.city,
            "industry": c.industry,
            "scale": c.scale,
            "website": c.website,
            "notes": c.notes,
            "created_at": c.created_at,
            "application_count": counts.get(c.id, 0),
        }
        result.append(item)
    return result


def search_by_keyword(db: Session, keyword: str, limit: int = 10):
    """公司名/别名联想（新增投递表单自动补全）。"""
    kw = f"%{keyword.strip()}%"
    rows = (
        company_repo.list_all(db, 0, 500) if not keyword else
        [
            c
            for c in company_repo.list_all(db, 0, 1000)
            if (c.name and keyword.lower() in c.name.lower())
            or (c.alias and keyword.lower() in c.alias.lower())
        ]
    )
    return rows[:limit]
