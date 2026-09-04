"""投递记录业务逻辑层（含全字段变更留痕，REQ-TRC-005）。"""
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import APPLICATION_STATUSES, APPLICATION_TYPES, FIELD_LABELS
from app.models.status_event import StatusEvent
from app.models.tag import Tag
from app.repositories import (
    application_repo,
    company_repo,
    resume_repo,
    status_event_repo,
    tag_repo,
)
from app.schemas.application import ApplicationCreate, ApplicationUpdate


def _check_type_status(type_: str | None, status: str | None) -> None:
    if type_ is not None and type_ not in APPLICATION_TYPES:
        raise HTTPException(status_code=400, detail=f"类型须为 {APPLICATION_TYPES}")
    if status is not None and status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail=f"状态须为 {APPLICATION_STATUSES}")


def _fmt(v) -> str | None:
    """将字段值转为可展示文本。"""
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return str(v)


def _record_create_event(db: Session, application_id: int, source: str) -> None:
    status_event_repo.create(
        db,
        application_id=application_id,
        event_type="创建记录",
        description="创建投递记录",
        source=source,
        event_time=datetime.now(),
    )
    db.commit()


def create_application(db: Session, data: ApplicationCreate, source: str = "用户操作"):
    _check_type_status(data.type, data.status)
    if not company_repo.get(db, data.company_id):
        raise HTTPException(status_code=404, detail="关联公司不存在")
    if data.resume_id and not resume_repo.get(db, data.resume_id):
        raise HTTPException(status_code=404, detail="关联简历不存在")
    obj = application_repo.create(db, data)

    # 创建时可同时打标签（自由输入，自动建档）
    if data.tag_names:
        tags = _ensure_tags(db, data.tag_names)
        application_repo.set_tags(db, obj, tags)

    _record_create_event(db, obj.id, source)
    return obj


def _ensure_tags(db: Session, names: list[str]) -> list[Tag]:
    """按名称取标签，不存在则自动创建。"""
    tags: list[Tag] = []
    for name in dict.fromkeys(n.strip() for n in names if n.strip()):
        t = tag_repo.get_by_name(db, name)
        if not t:
            t = tag_repo.create(db, name=name)
        tags.append(t)
    return tags


def get_or_404(db: Session, id: int):
    obj = application_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="投递记录不存在")
    return obj


def list_applications(db: Session, **filters):
    return application_repo.list_all(db, **filters)


def update_application(
    db: Session, id: int, data: ApplicationUpdate, source: str = "用户操作"
):
    obj = get_or_404(db, id)
    upd = data.model_dump(exclude_unset=True)
    _check_type_status(upd.get("type"), upd.get("status"))
    if upd.get("resume_id") and not resume_repo.get(db, upd["resume_id"]):
        raise HTTPException(status_code=404, detail="关联简历不存在")

    # 逐字段对比，生成变更事件（一次改多字段 → 各记一条）
    changes: list[tuple[str, object, object]] = []
    for k, v in upd.items():
        if k not in FIELD_LABELS:
            continue
        old = getattr(obj, k)
        if old != v:
            changes.append((k, old, v))

    if not changes:
        return obj

    now = datetime.now()
    for k, old, new in changes:
        status_event_repo.create(
            db,
            application_id=obj.id,
            event_type="状态变更" if k == "status" else "字段变更",
            field_name=FIELD_LABELS[k],
            old_value=_fmt(old),
            new_value=_fmt(new),
            source=source,
            event_time=now,
        )

    application_repo.update(db, obj, data)
    return obj


def set_application_tags(db: Session, id: int, names: list[str]):
    obj = get_or_404(db, id)
    tags = _ensure_tags(db, names)
    application_repo.set_tags(db, obj, tags)
    db.refresh(obj)
    return obj


def delete_application(db: Session, id: int) -> None:
    """软删除：置 deleted_at，可从回收站恢复（REQ-NFR-008）。"""
    obj = get_or_404(db, id)
    application_repo.soft_delete(db, obj)


def restore_application(db: Session, id: int):
    obj = get_or_404(db, id)
    application_repo.restore(db, obj)
    return obj


def build_timeline(
    db: Session,
    application_id: int,
    event_kind: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> list[dict]:
    """统一时间线：状态事件 + 沟通记录 + 附件 + 简历 + 问题混排（REQ-TRC-004）。

    event_kind 过滤：status / field / communication / attachment / issue，空为全部。
    """
    from app.models.attachment import Attachment
    from app.models.communication import Communication
    from app.models.issue import Issue
    from app.models.resume import Resume

    items: list[dict] = []

    for e in status_event_repo.list_by_application(db, application_id, limit=1000):
        kind = {
            "状态变更": "status",
            "字段变更": "field",
            "创建记录": "create",
        }.get(e.event_type, "field")
        items.append(
            {
                "kind": kind,
                "time": e.event_time,
                "id": e.id,
                "application_id": e.application_id,
                "event_type": e.event_type,
                "field_name": e.field_name,
                "old_value": e.old_value,
                "new_value": e.new_value,
                "source": e.source,
                "description": e.description,
            }
        )

    from app.repositories import communication_repo

    for c in communication_repo.list_by_application(
        db, application_id, limit=1000
    ):
        items.append(
            {
                "kind": "communication",
                "time": c.occurred_at,
                "id": c.id,
                "application_id": c.application_id,
                "contact": c.contact,
                "method": c.method,
                "content": c.content,
                "my_action": c.my_action,
            }
        )

    for a in (
        db.query(Attachment)
        .filter(Attachment.application_id == application_id)
        .all()
    ):
        items.append(
            {
                "kind": "attachment",
                "time": a.uploaded_at,
                "id": a.id,
                "filename": a.filename,
                "att_type": a.att_type,
            }
        )

    for r in (
        db.query(Resume)
        .filter(Resume.application_id == application_id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    ):
        items.append(
            {
                "kind": "resume",
                "time": r.uploaded_at,
                "id": r.id,
                "filename": r.filename,
                "att_type": r.version or "简历",
            }
        )

    for i in (
        db.query(Issue)
        .filter(Issue.related_application_id == application_id)
        .order_by(Issue.created_at.desc())
        .all()
    ):
        items.append(
            {
                "kind": "issue",
                "time": i.created_at,
                "id": i.id,
                "title": i.title,
                "description": i.description,
            }
        )

    # 时间倒序混排（None 时间排最后）
    items.sort(key=lambda x: x.get("time") or datetime.min, reverse=True)

    if event_kind:
        items = [i for i in items if i["kind"] == event_kind]

    return items[offset : offset + limit]
