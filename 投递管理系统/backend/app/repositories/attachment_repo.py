"""附件数据访问层。"""
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


def create(
    db: Session,
    *,
    application_id: int,
    filename: str,
    object_key: str,
    size: int | None = None,
    content_type: str | None = None,
    att_type: str = "其他",
) -> Attachment:
    obj = Attachment(
        application_id=application_id,
        filename=filename,
        object_key=object_key,
        size=size,
        content_type=content_type,
        att_type=att_type,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Attachment | None:
    return db.get(Attachment, id)


def list_by_application(db: Session, application_id: int) -> list[Attachment]:
    return (
        db.query(Attachment)
        .filter(Attachment.application_id == application_id)
        .order_by(Attachment.uploaded_at.desc(), Attachment.id.desc())
        .all()
    )


def update(db: Session, obj: Attachment, att_type: str) -> Attachment:
    obj.att_type = att_type
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Attachment) -> None:
    db.delete(obj)
    db.commit()
