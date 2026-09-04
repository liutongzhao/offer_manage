"""简历资产数据访问层。"""
from sqlalchemy.orm import Session

from app.models.resume import Resume


def create(
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
) -> Resume:
    obj = Resume(
        filename=filename,
        object_key=object_key,
        size=size,
        content_type=content_type,
        company=company,
        application_id=application_id,
        is_base=is_base,
        version=version,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Resume | None:
    return db.get(Resume, id)


def list_all(db: Session, skip: int = 0, limit: int = 100) -> list[Resume]:
    return db.query(Resume).order_by(Resume.id.desc()).offset(skip).limit(limit).all()


def delete(db: Session, obj: Resume) -> None:
    db.delete(obj)
    db.commit()
