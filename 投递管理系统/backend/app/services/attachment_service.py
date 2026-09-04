"""附件业务逻辑层。"""
import os
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import ATTACHMENT_TYPES
from app.repositories import attachment_repo
from app.schemas.attachment import AttachmentOut
from app.storage import minio_client


def guess_type(filename: str) -> str:
    """根据扩展名猜测附件默认类型（UI 交互 IX-06）。"""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
        return "JD截图"
    if ext == ".pdf":
        return "简历"
    return "其他"


def create_attachment(
    db: Session,
    *,
    application_id: int,
    file,
    att_type: str | None = None,
) -> AttachmentOut:
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="空文件")
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="单个文件不能超过 20MB")
    if att_type and att_type not in ATTACHMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"附件类型须为 {ATTACHMENT_TYPES}")
    final_type = att_type or guess_type(file.filename)
    ext = os.path.splitext(file.filename or "")[1]
    object_key = f"附件/{application_id}/{uuid.uuid4().hex}{ext}"
    minio_client.upload_file(object_key, data, file.content_type)
    rec = attachment_repo.create(
        db,
        application_id=application_id,
        filename=file.filename or "未命名文件",
        object_key=object_key,
        size=len(data),
        content_type=file.content_type,
        att_type=final_type,
    )
    return AttachmentOut.model_validate(rec)


def get_or_404(db: Session, id: int):
    obj = attachment_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="附件不存在")
    return obj


def update_attachment(db: Session, id: int, att_type: str | None):
    obj = get_or_404(db, id)
    if att_type is not None:
        if att_type not in ATTACHMENT_TYPES:
            raise HTTPException(
                status_code=400, detail=f"附件类型须为 {ATTACHMENT_TYPES}"
            )
        return attachment_repo.update(db, obj, att_type)
    return obj


def delete_attachment(db: Session, id: int) -> None:
    obj = get_or_404(db, id)
    try:
        minio_client.delete_file(obj.object_key)
    except Exception:
        # 对象已不存在不影响记录删除
        pass
    attachment_repo.delete(db, obj)
