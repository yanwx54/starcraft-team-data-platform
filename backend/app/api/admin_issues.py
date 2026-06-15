"""后台管理接口 — 数据异常中心。"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.data_issue import DataIssue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/issues", tags=["admin-issues"])


@router.get("")
def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    issue_type: str | None = None,
    status: str | None = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """异常列表。"""
    query = db.query(DataIssue)
    if issue_type:
        query = query.filter(DataIssue.issue_type == issue_type)
    if status:
        query = query.filter(DataIssue.status == status)

    total = query.count()
    items = (
        query.order_by(DataIssue.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": issue.id,
                "issue_type": issue.issue_type,
                "source_table": issue.source_table,
                "source_id": issue.source_id,
                "description": issue.description,
                "status": issue.status,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            }
            for issue in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{issue_id}")
def get_issue_detail(
    issue_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """异常详情。"""
    issue = db.query(DataIssue).filter(DataIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    return {
        "id": issue.id,
        "issue_type": issue.issue_type,
        "source_table": issue.source_table,
        "source_id": issue.source_id,
        "description": issue.description,
        "status": issue.status,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
    }


class ResolveRequest(BaseModel):
    resolution_note: str | None = None


@router.patch("/{issue_id}/resolve")
def resolve_issue(
    issue_id: int,
    request: ResolveRequest | None = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """标记异常为已解决。"""
    issue = db.query(DataIssue).filter(DataIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    issue.status = "resolved"
    db.commit()
    db.refresh(issue)
    logger.info("管理员 %s 解决异常: issue_id=%d", current_admin.username, issue_id)
    return {
        "id": issue.id,
        "status": issue.status,
        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
    }


@router.patch("/{issue_id}/reopen")
def reopen_issue(
    issue_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """重新打开异常。"""
    issue = db.query(DataIssue).filter(DataIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="异常记录不存在")
    issue.status = "open"
    db.commit()
    db.refresh(issue)
    logger.info("管理员 %s 重新打开异常: issue_id=%d", current_admin.username, issue_id)
    return {
        "id": issue.id,
        "status": issue.status,
        "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
    }
