"""应用入口：装配路由、CORS、生命周期。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
