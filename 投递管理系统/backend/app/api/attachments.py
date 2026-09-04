"""附件路由层（上传 / 预览 / 类型标注 / 删除）。"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.repositories import application_repo
from app.schemas.attachment import AttachmentOut, AttachmentUpdate
from app.schemas.common import ApiResponse
from app.services import attachment_service
from app.storage import minio_client

router = APIRouter(prefix="/api/v1", tags=["附件"])


@router.post(
    "/applications/{application_id}/attachments",
    response_model=ApiResponse[AttachmentOut],
)
def upload(
    application_id: int,
    file: UploadFile = File(...),
    att_type: str = Form(None),
    db: Session = Depends(get_db),
):
    if not application_repo.get(db, application_id):
        raise HTTPException(status_code=404, detail="投递记录不存在")
    rec = attachment_service.create_attachment(
        db, application_id=application_id, file=file, att_type=att_type
    )
    return ApiResponse(data=rec)


@router.get(
    "/applications/{application_id}/attachments",
    response_model=ApiResponse[list[AttachmentOut]],
)
def list_by_application(application_id: int, db: Session = Depends(get_db)):
    from app.repositories import attachment_repo

    return ApiResponse(
        data=[
            AttachmentOut.model_validate(i)
            for i in attachment_repo.list_by_application(db, application_id)
        ]
    )


@router.get("/attachments/{id}/url", response_model=ApiResponse[str])
def get_url(id: int, db: Session = Depends(get_db)):
    obj = attachment_service.get_or_404(db, id)
    return ApiResponse(data=minio_client.get_presigned_url(obj.object_key))


@router.patch("/attachments/{id}", response_model=ApiResponse[AttachmentOut])
def update(id: int, data: AttachmentUpdate, db: Session = Depends(get_db)):
    return ApiResponse(
        data=AttachmentOut.model_validate(
            attachment_service.update_attachment(db, id, data.att_type)
        )
    )


@router.delete("/attachments/{id}", response_model=ApiResponse[None])
def delete(id: int, db: Session = Depends(get_db)):
    attachment_service.delete_attachment(db, id)
    return ApiResponse(data=None)
