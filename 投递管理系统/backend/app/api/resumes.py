"""简历资产路由层（文件上传 / 预览 / 删除）。"""
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.resume import ResumeOut
from app.services import resume_service
from app.storage import minio_client

router = APIRouter(prefix="/api/v1/resumes", tags=["简历"])


@router.post("", response_model=ApiResponse[ResumeOut])
def upload(
    file: UploadFile = File(...),
    company: str = Form(None),
    application_id: int = Form(None),
    is_base: bool = Form(False),
    version: str = Form(None),
    db: Session = Depends(get_db),
):
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="空文件")
    ext = os.path.splitext(file.filename or "")[1]
    prefix = "初始简历" if is_base else (company or "通用")
    object_key = f"{prefix}/{uuid.uuid4().hex}{ext}"
    minio_client.upload_file(object_key, data, file.content_type)
    rec = resume_service.create_resume(
        db,
        filename=file.filename,
        object_key=object_key,
        size=len(data),
        content_type=file.content_type,
        company=company,
        application_id=application_id,
        is_base=is_base,
        version=version,
    )
    return ApiResponse(data=ResumeOut.model_validate(rec))


@router.get("", response_model=ApiResponse[list[ResumeOut]])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from app.repositories import resume_repo

    items = resume_repo.list_all(db, skip, limit)
    return ApiResponse(data=[ResumeOut.model_validate(i) for i in items])


@router.get("/{id}/url", response_model=ApiResponse[str])
def get_url(id: int, db: Session = Depends(get_db)):
    obj = resume_service.get_or_404(db, id)
    return ApiResponse(data=minio_client.get_presigned_url(obj.object_key))


@router.delete("/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    resume_service.delete_resume(db, id)
    return ApiResponse(data=None)
