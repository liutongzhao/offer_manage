"""数据导入导出与备份恢复业务逻辑层（REQ-DATA-001/002/003）。"""
import csv
import io
import os
import shutil
import tempfile
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import (
    APPLICATION_STATUSES,
    APPLICATION_TYPES,
    CSV_COLUMNS,
)
from app.core.db import DB_PATH
from app.repositories import application_repo, company_repo
from app.services import application_service
from app.schemas.application import ApplicationCreate
from app.storage import minio_client

BACKUP_PREFIX = "备份/"


# ---------- 导出 ----------

def export_csv(db: Session, **filters) -> bytes:
    """导出投递明细为 CSV（UTF-8 BOM，Excel 打开中文不乱码）。导出绕过分页。"""
    _, items = application_repo.list_all(db, skip=0, limit=100000, **filters)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([cn for cn, _ in CSV_COLUMNS])
    for app in items:
        row_map = {
            "company_name": app.company.name if app.company else "",
            "type": app.type or "",
            "position": app.position or "",
            "status": app.status or "",
            "channel": app.channel or "",
            "city": app.city or "",
            "apply_date": app.apply_date.isoformat() if app.apply_date else "",
            "deadline": app.deadline.isoformat() if app.deadline else "",
            "interview_stage": app.interview_stage or "",
            "result_date": app.result_date.isoformat() if app.result_date else "",
            "salary": app.salary or "",
            "referrer": app.referrer or "",
            "tags": "、".join(t.name for t in app.tags),
            "notes": app.notes or "",
        }
        writer.writerow([row_map.get(attr, "") for _, attr in CSV_COLUMNS])
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


def total_limit(filters: dict) -> int:
    """导出时绕过分页，取足够大的条数。"""
    return 100000


# ---------- 导入 ----------

_REQUIRED = ["公司名称", "投递类型", "岗位名称"]


def import_csv(db: Session, content: bytes) -> dict:
    """批量导入投递（带校验），返回成功/失败明细。"""
    text = None
    for enc in ("utf-8-sig", "gbk", "utf-8"):
        try:
            text = content.decode(enc)
            break
        except (UnicodeDecodeError, ValueError):
            continue
    if text is None:
        raise HTTPException(status_code=400, detail="无法识别文件编码，请使用 UTF-8 或 GBK 编码的 CSV")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 文件为空或表头缺失")

    success, failures = 0, []
    for idx, row in enumerate(reader, start=2):  # 数据从第 2 行开始
        # 去除表头/取值空白
        row = { (k or "").strip(): (v or "").strip() for k, v in row.items() if k }
        errors: list[str] = []
        for col in _REQUIRED:
            if not row.get(col):
                errors.append(f"缺少必填列「{col}」")
        if errors:
            failures.append({"row": idx, "error": "；".join(errors)})
            continue

        type_ = row.get("投递类型", "")
        if type_ not in APPLICATION_TYPES:
            failures.append({"row": idx, "error": f"投递类型「{type_}」须为 {APPLICATION_TYPES}"})
            continue
        status = row.get("当前状态") or "待投递"
        if status not in APPLICATION_STATUSES:
            failures.append({"row": idx, "error": f"状态「{status}」须为 {APPLICATION_STATUSES}"})
            continue

        company_name = row["公司名称"]
        company = company_repo.get_by_name(db, company_name)
        if not company:
            from app.schemas.company import CompanyCreate

            company = company_repo.create(db, CompanyCreate(name=company_name))

        def _parse_date(s: str) -> date | None:
            if not s:
                return None
            return date.fromisoformat(s.replace("/", "-"))

        try:
            data = ApplicationCreate(
                company_id=company.id,
                type=type_,
                position=row["岗位名称"],
                status=status,
                channel=row.get("投递渠道") or None,
                city=row.get("工作城市") or None,
                apply_date=_parse_date(row.get("投递日期", "")),
                deadline=_parse_date(row.get("截止日期", "")),
                interview_stage=row.get("面试轮次") or None,
                result_date=_parse_date(row.get("结果日期", "")),
                salary=row.get("薪资范围") or None,
                referrer=row.get("内推人") or None,
                notes=row.get("备注") or None,
                tag_names=[t for t in (row.get("标签") or "").replace("，", "、").split("、") if t],
            )
            application_service.create_application(db, data, source="系统自动")
            success += 1
        except Exception as exc:  # 单行失败不影响其他行
            failures.append({"row": idx, "error": str(getattr(exc, "detail", exc))})
    return {"success_count": success, "fail_count": len(failures), "failures": failures}


# ---------- 备份 / 恢复 ----------

def backup_database() -> dict:
    """将 SQLite 库文件备份到 MinIO。"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=400, detail="数据库文件不存在，请先创建数据")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    object_key = f"{BACKUP_PREFIX}backup-{ts}.db"
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        shutil.copy2(DB_PATH, tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        minio_client.upload_file(object_key, data, "application/octet-stream")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return {"object_key": object_key, "size": len(data), "last_modified": ts}


def list_backups() -> list[dict]:
    client = minio_client.get_client()
    result = []
    for obj in client.list_objects(minio_client.BUCKET_NAME, prefix=BACKUP_PREFIX, recursive=True):
        result.append(
            {
                "object_key": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
            }
        )
    result.sort(key=lambda x: x["object_key"], reverse=True)
    return result


def restore_database(object_key: str) -> dict:
    """从 MinIO 备份恢复 SQLite 库文件（覆盖本地库，恢复后需重启服务）。"""
    if not object_key.startswith(BACKUP_PREFIX):
        raise HTTPException(status_code=400, detail="仅允许恢复「备份/」目录下的备份文件")
    try:
        data = minio_client.download_file(object_key)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"备份文件不存在或读取失败：{exc}")
    if not data:
        raise HTTPException(status_code=400, detail="备份文件为空")
    shutil.copy2(DB_PATH, DB_PATH + ".bak-before-restore")
    with open(DB_PATH, "wb") as f:
        f.write(data)
    return {
        "restored": True,
        "object_key": object_key,
        "message": "恢复完成，请重启后端服务后刷新页面",
    }
