"""pytest 全局夹具：独立临时 SQLite，不污染真实 app.db。

通过在导入 app 之前设置 SQLITE_PATH 环境变量，将数据库指向临时目录；
MinIO 依赖在各测试文件内按需 mock，不依赖真实 MinIO 服务。
"""
import itertools
import os
import sys
import tempfile

# 必须在导入 app 之前设置环境变量与 sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)

_TMP_DIR = tempfile.mkdtemp(prefix="qa_offer_test_")
os.environ["SQLITE_PATH"] = os.path.join(_TMP_DIR, "qa_test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import SessionLocal, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402


def envelope(resp):
    """断言统一信封结构并返回 data。"""
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body) >= {"code", "message", "data"}, f"响应缺少统一信封: {body}"
    assert body["code"] == 0, f"业务码非 0: {body}"
    return body["data"]


@pytest.fixture(scope="session")
def client():
    """TestClient：手动 init_db，不进入 lifespan（避免依赖真实 MinIO）。"""
    init_db()
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """每个用例结束后清空所有表，保证用例独立幂等。"""
    yield
    session = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()


_company_seq = itertools.count(1)
_app_seq = itertools.count(1)


@pytest.fixture
def make_company(client):
    """公司工厂：默认唯一名称，可覆盖字段。"""

    def _make(name: str | None = None, **kw) -> dict:
        if name is None:
            name = f"测试公司{next(_company_seq)}"
        payload = {"name": name, **kw}
        return envelope(client.post("/api/v1/companies", json=payload))

    return _make


@pytest.fixture
def make_application(client, make_company):
    """投递工厂：默认自动建公司，可覆盖任意字段。"""

    def _make(**kw) -> dict:
        if "company_id" not in kw:
            kw["company_id"] = make_company()["id"]
        payload = {"type": "后端开发", "position": f"岗位{next(_app_seq)}", **kw}
        return envelope(client.post("/api/v1/applications", json=payload))

    return _make
