"""公司路由层（含投递数聚合）。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate
from app.services import company_service

router = APIRouter(prefix="/api/v1/companies", tags=["公司"])


@router.post("", response_model=ApiResponse[CompanyOut])
def create(data: CompanyCreate, db: Session = Depends(get_db)):
    return ApiResponse(data=CompanyOut.model_validate(company_service.create_company(db, data)))


@router.get("", response_model=ApiResponse[list])
def list_all(
    with_count: bool = Query(True, description="是否附带投递数聚合"),
    keyword: str | None = Query(None, description="公司名/别名模糊搜索"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if with_count:
        items = company_service.list_with_count(db, skip, limit)
        if keyword:
            kw = keyword.strip().lower()
            items = [
                i
                for i in items
                if kw in (i["name"] or "").lower()
                or kw in (i.get("alias") or "").lower()
            ]
        return ApiResponse(data=items)
    items = company_service.list_companies(db, skip, limit)
    return ApiResponse(data=[CompanyOut.model_validate(i) for i in items])


@router.get("/{id}", response_model=ApiResponse[CompanyOut])
def get_one(id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=CompanyOut.model_validate(company_service.get_or_404(db, id)))


@router.patch("/{id}", response_model=ApiResponse[CompanyOut])
def update(id: int, data: CompanyUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=CompanyOut.model_validate(company_service.update_company(db, id, data))
    )


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    company_service.delete_company(db, id)
    return ApiResponse(data=None)
