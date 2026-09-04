"""简历资产业务逻辑层。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import resume_repo
from app.storage import minio_client


def create_resume(
    db: Session,
    *,
    filename: str,
    object_key: str,
    size: int | None = None,
    content_type: str | None = None,
    company: str | None = None,
    application_id: int | None = None,
    is_base: bool = False,
    version: str | None = None,
):
    return resume_repo.create(
        db,
        filename=filename,
        object_key=object_key,
        size=size,
        content_type=content_type,
        company=company,
        application_id=application_id,
        is_base=is_base,
        version=version,
    )


def get_or_404(db: Session, id: int):
    obj = resume_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="简历记录不存在")
    return obj


def delete_resume(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    try:
        minio_client.delete_file(obj.object_key)
    except Exception:
        # 对象已不存在不影响记录删除
        pass
    resume_repo.delete(db, obj)
