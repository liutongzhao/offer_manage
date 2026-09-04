"""应用入口：装配路由、CORS、生命周期、统一异常响应。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    analytics,
    applications,
    attachments,
    companies,
    communications,
    data,
    issues,
    links,
    resumes,
    tags,
)
from app.core.config import settings
from app.core.db import init_db
from app.core.logging import logger
from app.storage import minio_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    minio_client.get_client()  # 确保桶存在
    logger.info("秋招投递管理平台启动完成")
    yield


app = FastAPI(title="秋招投递管理平台", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (
    companies.router,
    applications.router,
    communications.router,
    links.router,
    attachments.router,
    resumes.router,
    issues.router,
    tags.router,
    analytics.router,
    data.router,
):
    app.include_router(r)


@app.get("/api/v1/health", tags=["系统"])
def health():
    return {"code": 0, "message": "ok", "data": {"status": "up"}}


# ---------- 统一错误信封（HTTPException / 422 校验错误均返回 {code, message, data}） ----------

def _envelope(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """业务/HTTP 错误包装为统一信封，保持原状态码不变。"""
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.status_code, str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求体/参数校验错误（422）：errors 摘要拼进 message，便于前端与代理定位。"""
    parts = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x not in ("body", "query", "path"))
        parts.append(f"{loc}: {err.get('msg', '')}" if loc else str(err.get("msg", "")))
    message = "参数校验失败：" + "；".join(parts) if parts else "参数校验失败"
    return JSONResponse(
        status_code=422,
        content=_envelope(422, message),
    )
