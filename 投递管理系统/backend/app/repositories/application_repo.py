"""投递记录数据访问层（多条件组合筛选 + 关键词搜索，REQ-SRCH-001/002）。"""
from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.application import Application
from app.models.company import Company
from app.models.tag import Tag, application_tag
from app.schemas.application import ApplicationCreate, ApplicationUpdate

# 允许排序的字段白名单
_SORTABLE = {
    "id": Application.id,
    "apply_date": Application.apply_date,
    "deadline": Application.deadline,
    "created_at": Application.created_at,
    "updated_at": Application.updated_at,
    "status": Application.status,
}


def create(db: Session, data: ApplicationCreate) -> Application:
    payload = data.model_dump(exclude={"tag_names"})
    obj = Application(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Application | None:
    return (
        db.query(Application)
        .options(joinedload(Application.company), joinedload(Application.tags))
        .filter(Application.id == id)
        .first()
    )


def list_all(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    type: str | None = None,
    status: str | None = None,
    channel: str | None = None,
    city: str | None = None,
    company_id: int | None = None,
    referrer: str | None = None,
    keyword: str | None = None,
    tag: str | None = None,
    apply_date_from: date | None = None,
    apply_date_to: date | None = None,
    deadline_from: date | None = None,
    deadline_to: date | None = None,
    archived: bool = False,
    include_deleted: bool = False,
    sort_by: str = "id",
    order: str = "desc",
) -> tuple[int, list[Application]]:
    """多条件组合筛选。返回 (总数, 当前页数据)。"""
    q = db.query(Application).options(
        joinedload(Application.company), joinedload(Application.tags)
    )

    # 软删除过滤
    if not include_deleted:
        q = q.filter(Application.deleted_at.is_(None))
    # 归档过滤：默认只看未归档；archived=True 只看已归档
    q = q.filter(Application.archived == archived)

    if type:
        q = q.filter(Application.type == type)
    if status:
        # 支持逗号分隔多状态
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        if statuses:
            q = q.filter(Application.status.in_(statuses))
    if channel:
        q = q.filter(Application.channel == channel)
    if city:
        q = q.filter(Application.city == city)
    if company_id:
        q = q.filter(Application.company_id == company_id)
    if referrer:
        q = q.filter(Application.referrer == referrer)
    if apply_date_from:
        q = q.filter(Application.apply_date >= apply_date_from)
    if apply_date_to:
        q = q.filter(Application.apply_date <= apply_date_to)
    if deadline_from:
        q = q.filter(Application.deadline >= deadline_from)
    if deadline_to:
        q = q.filter(Application.deadline <= deadline_to)

    # 关键词模糊搜索：公司名 / 别名 / 岗位 / 备注 / 招聘要求
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.join(Company, Application.company_id == Company.id).filter(
            or_(
                Company.name.ilike(kw),
                Company.alias.ilike(kw),
                Application.position.ilike(kw),
                Application.notes.ilike(kw),
                Application.requirements.ilike(kw),
            )
        )

    # 标签筛选
    if tag:
        q = (
            q.join(application_tag, Application.id == application_tag.c.application_id)
            .join(Tag, Tag.id == application_tag.c.tag_id)
            .filter(Tag.name == tag)
        )

    total = q.order_by(None).count()

    sort_col = _SORTABLE.get(sort_by, Application.id)
    if order == "asc":
        q = q.order_by(sort_col.asc(), Application.id.asc())
    else:
        q = q.order_by(sort_col.desc(), Application.id.desc())

    items = q.offset(skip).limit(limit).all()
    return total, items


def update(db: Session, obj: Application, data: ApplicationUpdate) -> Application:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def soft_delete(db: Session, obj: Application) -> None:
    from datetime import datetime

    obj.deleted_at = datetime.now()
    db.commit()


def restore(db: Session, obj: Application) -> None:
    obj.deleted_at = None
    db.commit()


def hard_delete(db: Session, obj: Application) -> None:
    db.delete(obj)
    db.commit()


def set_tags(db: Session, obj: Application, tag_objs: list[Tag]) -> None:
    obj.tags = tag_objs
    db.commit()


def count_by_company(db: Session) -> dict[int, int]:
    """按公司聚合投递数（未删除记录）。"""
    from sqlalchemy import func

    rows = (
        db.query(Application.company_id, func.count(Application.id))
        .filter(Application.deleted_at.is_(None))
        .group_by(Application.company_id)
        .all()
    )
    return {company_id: cnt for company_id, cnt in rows}


def distinct_cities(db: Session) -> list[str]:
    """筛选项：出现过的城市。"""
    rows = (
        db.query(Application.city)
        .filter(Application.city.isnot(None), Application.deleted_at.is_(None))
        .distinct()
        .all()
    )
    return sorted({r[0] for r in rows if r[0]})
