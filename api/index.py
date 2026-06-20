"""Vercel Serverless Function 入口 — 简化版，确保能正常响应。"""

import sys
import os

# 项目根目录是 Vercel 的工作目录
# backend/ 目录就在工作目录中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# 确保 backend 目录在 Python 路径中
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

# 数据库连接（使用环境变量 DATABASE_URL）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://starcraft:starcraft123@localhost:5432/starcraft",
)

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_CONNECTED = True
except Exception:
    DB_CONNECTED = False


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 从 backend 导入路由
from app.api import dashboard, matches, players, teams, maps, seasons, rankings, search
from app.api import admin_auth, admin_crawler, admin_backfill, admin_issues, admin_translations

app = FastAPI(
    title="StarCraft Team Data Platform",
    description="韩国星际争霸团战数据自动采集与统计平台",
    version="1.0.0",
)

# 注册所有路由
app.include_router(dashboard.router)
app.include_router(matches.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(maps.router)
app.include_router(seasons.router)
app.include_router(rankings.router)
app.include_router(search.router)
app.include_router(admin_auth.router)
app.include_router(admin_crawler.router)
app.include_router(admin_backfill.router)
app.include_router(admin_issues.router)
app.include_router(admin_translations.router)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "database": "ok" if DB_CONNECTED else "connection_failed",
        "crawler": "ok",
    }
