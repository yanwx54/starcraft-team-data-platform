"""后台管理接口 — 翻译规则 CRUD。"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.translation_rule import TranslationRule

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/translations", tags=["admin-translations"])


class TranslationCreateRequest(BaseModel):
    rule_type: str  # player / map
    source_text: str
    translated_text: str
    alias_group: str | None = None
    priority: int = 1


class TranslationUpdateRequest(BaseModel):
    rule_type: str | None = None
    source_text: str | None = None
    translated_text: str | None = None
    alias_group: str | None = None
    priority: int | None = None


@router.get("")
def list_translations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    rule_type: str | None = None,
    keyword: str | None = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """查看翻译规则列表。"""
    query = db.query(TranslationRule)
    if rule_type:
        query = query.filter(TranslationRule.rule_type == rule_type)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (TranslationRule.source_text.ilike(like))
            | (TranslationRule.translated_text.ilike(like))
        )

    total = query.count()
    items = (
        query.order_by(TranslationRule.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": r.id,
                "rule_type": r.rule_type,
                "source_text": r.source_text,
                "translated_text": r.translated_text,
                "alias_group": r.alias_group,
                "priority": r.priority,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
def create_translation(
    request: TranslationCreateRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """新增翻译规则。"""
    existing = (
        db.query(TranslationRule)
        .filter(
            TranslationRule.rule_type == request.rule_type,
            TranslationRule.source_text == request.source_text,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="该翻译规则已存在")

    rule = TranslationRule(
        rule_type=request.rule_type,
        source_text=request.source_text,
        translated_text=request.translated_text,
        alias_group=request.alias_group,
        priority=request.priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    logger.info("管理员 %s 新增翻译规则: id=%d", current_admin.username, rule.id)
    return {
        "id": rule.id,
        "rule_type": rule.rule_type,
        "source_text": rule.source_text,
        "translated_text": rule.translated_text,
        "alias_group": rule.alias_group,
        "priority": rule.priority,
    }


@router.put("/{rule_id}")
def update_translation(
    rule_id: int,
    request: TranslationUpdateRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """修改翻译规则。"""
    rule = db.query(TranslationRule).filter(TranslationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="翻译规则不存在")

    if request.rule_type is not None:
        rule.rule_type = request.rule_type
    if request.source_text is not None:
        rule.source_text = request.source_text
    if request.translated_text is not None:
        rule.translated_text = request.translated_text
    if request.alias_group is not None:
        rule.alias_group = request.alias_group
    if request.priority is not None:
        rule.priority = request.priority

    db.commit()
    db.refresh(rule)
    logger.info("管理员 %s 修改翻译规则: id=%d", current_admin.username, rule_id)
    return {
        "id": rule.id,
        "rule_type": rule.rule_type,
        "source_text": rule.source_text,
        "translated_text": rule.translated_text,
        "alias_group": rule.alias_group,
        "priority": rule.priority,
    }


@router.delete("/{rule_id}")
def delete_translation(
    rule_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """删除翻译规则。"""
    rule = db.query(TranslationRule).filter(TranslationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="翻译规则不存在")

    db.delete(rule)
    db.commit()
    logger.info("管理员 %s 删除翻译规则: id=%d", current_admin.username, rule_id)
    return {"message": "翻译规则已删除"}
