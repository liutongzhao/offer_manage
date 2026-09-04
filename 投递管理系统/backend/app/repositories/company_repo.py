"""公司数据访问层。"""
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def create(db: Session, data: CompanyCreate) -> Company:
    obj = Company(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, id: int) -> Company | None:
    return db.get(Company, id)


def get_by_name(db: Session, name: str) -> Company | None:
    return db.query(Company).filter(Company.name == name).first()


def list_all(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    return (
        db.query(Company)
        .order_by(Company.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update(db: Session, obj: Company, data: CompanyUpdate) -> Company:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Company) -> None:
    db.delete(obj)
    db.commit()
