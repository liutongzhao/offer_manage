"""标签业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import TAG_SCOPES
from app.repositories import tag_repo


def create_tag(db: Session, name: str, scope: str = "投递", color: str | None = None):
    if scope not in TAG_SCOPES:
        raise HTTPException(status_code=400, detail=f"适用对象须为 {TAG_SCOPES}")
    if tag_repo.get_by_name(db, name):
        raise HTTPException(status_code=400, detail=f"标签「{name}」已存在")
    return tag_repo.create(db, name=name, scope=scope, color=color)


def get_or_404(db: Session, id: int):
    obj = tag_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="标签不存在")
    return obj


def list_tags(db: Session):
    return tag_repo.list_all(db)


def list_tags_with_count(db: Session):
    tags = tag_repo.list_all(db)
    counts = tag_repo.usage_counts(db)
    return [
        {
            "id": t.id,
            "name": t.name,
            "scope": t.scope,
            "color": t.color,
            "usage_count": counts.get(t.id, 0),
        }
        for t in tags
    ]


def update_tag(db: Session, id: int, name: str | None, color: str | None):
    obj = get_or_404(db, id)
    if name and name != obj.name:
        existed = tag_repo.get_by_name(db, name)
        if existed:
            raise HTTPException(status_code=400, detail=f"标签「{name}」已存在")
    return tag_repo.update(db, obj, name, color)


def delete_tag(db: Session, id: int) -> None:
    """删除标签不影响已关联记录（自动解绑）。"""
    obj = get_or_404(db, id)
    tag_repo.delete(db, obj)
