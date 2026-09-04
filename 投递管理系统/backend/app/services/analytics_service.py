"""统计分析业务逻辑层（汇总 / 漏斗 / 趋势 / 待办 / 近期动态）。"""
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import TERMINAL_STATUSES
from app.models.application import Application
from app.models.attachment import Attachment
from app.models.company import Company
from app.models.communication import Communication
from app.models.issue import Issue
from app.models.status_event import StatusEvent


def get_summary(db: Session) -> dict:
    total = (
        db.query(func.count(Application.id))
        .filter(Application.deleted_at.is_(None))
        .scalar()
        or 0
    )
    by_type = dict(
        db.query(Application.type, func.count(Application.id))
        .filter(Application.deleted_at.is_(None))
        .group_by(Application.type)
        .all()
    )
    by_status = dict(
        db.query(Application.status, func.count(Application.id))
        .filter(Application.deleted_at.is_(None))
        .group_by(Application.status)
        .all()
    )
    by_channel = dict(
        db.query(Application.channel, func.count(Application.id))
        .filter(
            Application.deleted_at.is_(None), Application.channel.isnot(None)
        )
        .group_by(Application.channel)
        .all()
    )
    issues_total = db.query(func.count(Issue.id)).scalar() or 0
    week_ago = date.today() - timedelta(days=7)
    week_count = (
        db.query(func.count(Application.id))
        .filter(
            Application.deleted_at.is_(None),
            Application.apply_date.isnot(None),
            Application.apply_date >= week_ago,
        )
        .scalar()
        or 0
    )
    interviewing = by_status.get("面试中", 0)
    offered = by_status.get("已Offer", 0)
    conversion = round(offered / total * 100, 1) if total else 0.0
    return {
        "total": total,
        "by_type": by_type,
        "by_status": by_status,
        "by_channel": by_channel,
        "issues_total": issues_total,
        "week_count": week_count,
        "interviewing": interviewing,
        "offered": offered,
        "conversion_rate": conversion,
    }


def get_funnel(db: Session) -> dict:
    """转化漏斗。

    口径（Q-6）：无历史状态轨迹时，以「当前状态所处阶梯位置」近似：
    分母 = 进入该环节总数（含已流出），
    阶梯：投递(非待投递) → 笔试(≥笔试中) → 面试(≥面试中) → Offer。
    终态记录（已挂/爽约/已拒绝）至少计入「投递」环节。
    """
    rows = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.deleted_at.is_(None))
        .group_by(Application.status)
        .all()
    )
    by_status = {s: c for s, c in rows}
    total_all = sum(by_status.values())
    pending = by_status.get("待投递", 0)

    ladder = [
        # 投递环节 = 全部记录 - 仍待投递（含已流出终态：已Offer/已挂/已拒绝/爽约），每条记录只计一次
        ("投递", total_all - pending),
        ("笔试", by_status.get("笔试中", 0) + by_status.get("面试中", 0)
         + by_status.get("已Offer", 0)),
        ("面试", by_status.get("面试中", 0) + by_status.get("已Offer", 0)),
        ("Offer", by_status.get("已Offer", 0)),
    ]
    base = ladder[0][1] if ladder[0][1] else 0
    stages = [
        {
            "stage": name,
            "count": count,
            "percent": round(count / base * 100, 1) if base else 0.0,
        }
        for name, count in ladder
    ]
    return {"stages": stages}


def get_trend(db: Session, granularity: str = "week", months: int = 6) -> list[dict]:
    """投递量时间趋势：按周（ISO 周）或按月聚合。"""
    start = date.today() - timedelta(days=months * 30)
    rows = (
        db.query(Application.apply_date)
        .filter(
            Application.deleted_at.is_(None),
            Application.apply_date.isnot(None),
            Application.apply_date >= start,
        )
        .all()
    )
    buckets: dict[str, int] = {}
    for (d,) in rows:
        if granularity == "month":
            key = d.strftime("%Y-%m")
        else:
            iso = d.isocalendar()
            key = f"{iso[0]}-W{iso[1]:02d}"
        buckets[key] = buckets.get(key, 0) + 1
    return [
        {"period": k, "count": v} for k, v in sorted(buckets.items())
    ]


def get_todos(db: Session) -> dict:
    """基于 deadline 的临期待办：7 天内截止 / 已过期（REQ-NFY-001/002）。"""
    today = date.today()
    deadline_soon = today + timedelta(days=7)
    rows = (
        db.query(Application, Company.name)
        .join(Company, Application.company_id == Company.id)
        .filter(
            Application.deleted_at.is_(None),
            Application.archived.is_(False),
            Application.deadline.isnot(None),
            Application.status.notin_(TERMINAL_STATUSES),
        )
        .all()
    )
    expired: list[dict] = []
    due_soon: list[dict] = []
    for app, company_name in rows:
        assert app.deadline is not None
        days_left = (app.deadline - today).days
        item = {
            "application_id": app.id,
            "company_name": company_name,
            "position": app.position,
            "status": app.status,
            "deadline": app.deadline,
            "days_left": days_left,
        }
        if days_left < 0:
            expired.append(item)
        elif days_left <= 7:
            due_soon.append(item)
    expired.sort(key=lambda x: x["days_left"])
    due_soon.sort(key=lambda x: x["days_left"])
    return {"expired": expired, "due_soon": due_soon}


def get_recent_events(db: Session, limit: int = 10) -> list[dict]:
    """全系统近期动态（看板展示）：状态/字段事件 + 沟通混排。"""
    events = (
        db.query(StatusEvent, Application, Company.name)
        .join(Application, StatusEvent.application_id == Application.id)
        .join(Company, Application.company_id == Company.id)
        .filter(Application.deleted_at.is_(None))
        .order_by(StatusEvent.event_time.desc())
        .limit(limit)
        .all()
    )
    comms = (
        db.query(Communication, Application, Company.name)
        .join(Application, Communication.application_id == Application.id)
        .join(Company, Application.company_id == Company.id)
        .filter(Application.deleted_at.is_(None))
        .order_by(Communication.occurred_at.desc())
        .limit(limit)
        .all()
    )
    items: list[dict] = []
    for e, app, company_name in events:
        if e.event_type == "状态变更":
            summary = f"状态 {e.old_value or '空'} → {e.new_value or '空'}"
        elif e.event_type == "创建记录":
            summary = "创建投递记录"
        else:
            summary = f"{e.field_name or ''}：{e.old_value or '空'} → {e.new_value or '空'}"
        items.append(
            {
                "kind": "event",
                "time": e.event_time.isoformat() if e.event_time else "",
                "application_id": app.id,
                "company_name": company_name,
                "position": app.position,
                "summary": summary,
            }
        )
    for c, app, company_name in comms:
        items.append(
            {
                "kind": "communication",
                "time": c.occurred_at.isoformat() if c.occurred_at else "",
                "application_id": app.id,
                "company_name": company_name,
                "position": app.position,
                "summary": f"{c.contact or '对方'} · {c.method}：{(c.content or '')[:40]}",
            }
        )
    items.sort(key=lambda x: x["time"], reverse=True)
    return items[:limit]
