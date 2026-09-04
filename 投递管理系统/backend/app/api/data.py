"""数据路由层：导出 CSV / 批量导入 / 备份与恢复。"""
from datetime import date
from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.data import BackupInfo, ImportResult, RestoreRequest
from app.services import data_service

router = APIRouter(prefix="/api/v1/data", tags=["数据"])


@router.get("/export/applications.csv")
def export_applications(
    type: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    city: str | None = None,
    company_id: int | None = None,
    keyword: str | None = None,
    tag: str | None = None,
    apply_date_from: date | None = None,
    apply_date_to: date | None = None,
    deadline_from: date | None = None,
    deadline_to: date | None = None,
    archived: bool = False,
    db: Session = Depends(get_db),
):
    """导出投递明细 CSV（当前筛选结果，UTF-8 BOM）。"""
    content = data_service.export_csv(
        db,
        type=type,
        status=status,
        channel=channel,
        city=city,
        company_id=company_id,
        keyword=keyword,
        tag=tag,
        apply_date_from=apply_date_from,
        apply_date_to=apply_date_to,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        archived=archived,
    )
    filename = f"投递明细-{date.today().isoformat()}.csv"
    from urllib.parse import quote

    quoted = quote(filename)
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=applications.csv; filename*=UTF-8''{quoted}"
        },
    )


@router.post("/import/applications", response_model=ApiResponse[ImportResult])
def import_applications(file: UploadFile, db: Session = Depends(get_db)):
    """CSV 批量导入投递（带校验，返回成功/失败明细）。"""
    content = file.file.read()
    result = data_service.import_csv(db, content)
    return ApiResponse(data=ImportResult(**result))


@router.post("/backup", response_model=ApiResponse[BackupInfo])
def backup(db: Session = Depends(get_db)):
    """备份 SQLite 库文件到 MinIO。"""
    return ApiResponse(data=data_service.backup_database())


@router.get("/backups", response_model=ApiResponse[list[BackupInfo]])
def backups(db: Session = Depends(get_db)):
    return ApiResponse(data=[BackupInfo(**b) for b in data_service.list_backups()])


@router.post("/restore", response_model=ApiResponse[dict])
def restore(data: RestoreRequest, db: Session = Depends(get_db)):
    """从备份恢复（覆盖本地库，恢复后需重启服务）。"""
    return ApiResponse(data=data_service.restore_database(data.object_key))
