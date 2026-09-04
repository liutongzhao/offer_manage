"""标签相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    scope: str = "投递"
    color: str | None = None


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    color: str | None = None


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    scope: str
    color: str | None = None


class TagWithCount(TagOut):
    """标签及关联投递数（标签管理页展示引用数）。"""

    usage_count: int = 0


class ApplicationTagsSet(BaseModel):
    """为投递设置标签（整体替换）。"""

    names: list[str]
