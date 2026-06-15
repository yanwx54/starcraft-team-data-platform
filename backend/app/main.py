import logging
from pathlib import Path

from fastapi import FastAPI

from app.database import SessionLocal
from app.models.admin_user import AdminUser
from app.translate.parser import parse_translate_rules
from app.translate.importer import import_rules_to_db
from app.api import dashboard, matches, players, teams, maps, seasons, rankings, search
from app.api import admin_auth, admin_crawler, admin_backfill, admin_issues, admin_translations

logger = logging.getLogger(__name__)

RULES_FILE = Path(__file__).resolve().parent.parent.parent / "translate_rules.md"

app = FastAPI(
    title="StarCraft Team Data Platform",
    description="韩国星际争霸团战数据自动采集与统计平台",
    version="1.0.0",
)

# 注册统计服务路由
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


@app.on_event("startup")
def startup_import_rules():
    """系统启动时读取 translate_rules.md 并导入数据库。"""
    try:
        rules = parse_translate_rules(RULES_FILE)
        db = SessionLocal()
        try:
            result = import_rules_to_db(db, rules)
            logger.info(
                "翻译规则导入完成: 新增 %d 条, 跳过 %d 条 (选手 %d, 地图 %d)",
                result["added"],
                result["skipped"],
                rules.player_count(),
                rules.map_count(),
            )
        finally:
            db.close()
    except FileNotFoundError:
        logger.warning("翻译规则文件未找到: %s", RULES_FILE)
    except Exception as e:
        logger.error("翻译规则导入失败: %s", e)


@app.on_event("startup")
def startup_seed_admin():
    """系统启动时确保默认管理员存在。"""
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            admin = AdminUser(
                username="admin",
                hashed_password="admin123",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("默认管理员已创建: admin / admin123")
        else:
            logger.info("管理员账号已存在")
    except Exception as e:
        logger.error("创建默认管理员失败: %s", e)
    finally:
        db.close()


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "database": "ok", "crawler": "ok"}
