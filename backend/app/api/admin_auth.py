"""管理员认证 — JWT 令牌签发与校验。"""

import os
import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin_user import AdminUser

logger = logging.getLogger(__name__)

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "starcraft-admin-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])

security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """简易密码校验（生产环境应使用 bcrypt）。"""
    return plain_password == hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """签发 JWT 令牌。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    """从 JWT 令牌中解析当前管理员。"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证凭据")

    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return admin


@router.post("/login", response_model=TokenResponse)
def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录，返回 JWT 令牌。"""
    admin = db.query(AdminUser).filter(AdminUser.username == request.username).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not _verify_password(request.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": admin.username})
    logger.info("管理员登录成功: %s", admin.username)
    return TokenResponse(access_token=access_token, username=admin.username)


@router.get("/me")
def admin_me(current_admin: AdminUser = Depends(get_current_admin)):
    """获取当前管理员信息。"""
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "is_active": current_admin.is_active,
    }
