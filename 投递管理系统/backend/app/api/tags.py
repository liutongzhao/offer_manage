"""标签路由层。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.repositories import tag_repo
from app.schemas.common import ApiResponse
from app.schemas.tag import TagCreate, TagUpdate
from app.services import tag_service

router = APIRouter(prefix="/api/v1/tags", tags=["标签"])


@router.post("", response_model=ApiResponse[dict])
def create(data: TagCreate, db: Session = Depends(get_db)):
    obj = tag_service.create_tag(db, data.name, data.scope, data.color)
    return ApiResponse(data={"id": obj.id, "name": obj.name, "scope": obj.scope, "color": obj.color, "usage_count": 0})


@router.get("", response_model=ApiResponse[list[dict]])
def list_all(db: Session = Depends(get_db)):
    return ApiResponse(data=tag_service.list_tags_with_count(db))


@router.patch("/{id}", response_model=ApiResponse[dict])
def update(id: int, data: TagUpdate, db: Session = Depends(get_db)):
    obj = tag_service.update_tag(db, id, data.name, data.color)
    counts = __import__("app.repositories.tag_repo", fromlist=["tag_repo"]).usage_counts(db)
    return ApiResponse(data={"id": obj.id, "name": obj.name, "scope": obj.scope, "color": obj.color, "usage_count": counts.get(obj.id, 0)})


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    tag_service.delete_tag(db, id)
    return ApiResponse(data=None)
