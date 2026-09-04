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


def update_resume(db: Session, id: int, fields: dict):
    """部分更新简历（如关联到投递）。fields 仅含显式传入的键。"""
    obj = get_or_404(db, id)
    if "application_id" in fields and fields["application_id"] is not None:
        from app.repositories import application_repo

        if not application_repo.get(db, fields["application_id"]):
            raise HTTPException(status_code=404, detail="投递记录不存在")
    return resume_repo.update(db, obj, fields)


def delete_resume(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    try:
        minio_client.delete_file(obj.object_key)
    except Exception:
        # 对象已不存在不影响记录删除
        pass
    resume_repo.delete(db, obj)
