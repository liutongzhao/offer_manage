"""数据库层：SQLAlchemy 引擎、会话、Base 与初始化。"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_db_path = settings.sqlite_path
if not os.path.isabs(_db_path):
    _db_path = os.path.join(BASE_DIR, _db_path)
os.makedirs(os.path.dirname(_db_path), exist_ok=True)

engine = create_engine(
    f"sqlite:///{_db_path}",
    connect_args={"check_same_thread": False},
)
# 数据库文件绝对路径（备份/恢复使用）
DB_PATH = _db_path
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # 导入模型以注册表结构
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
