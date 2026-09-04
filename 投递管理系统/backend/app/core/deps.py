"""依赖注入层：供路由复用。"""
from app.core.db import get_db

__all__ = ["get_db"]
