# models 包：导入各实体以注册到 Base.metadata
from app.models.base import Base  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.issue import Issue  # noqa: F401
