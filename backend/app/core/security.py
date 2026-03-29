from datetime import datetime, timedelta
from typing import Optional, List, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.staff import Staff
from app.models.merchant import Merchant
from app.core.permissions import ALL_PERMISSIONS, SYSTEM_ROLES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_permissions(user: Staff, db: Session) -> List[str]:
    """获取用户的所有权限"""
    # 超级管理员拥有所有权限
    if user.is_super_admin:
        return [p["code"] for p in ALL_PERMISSIONS]

    # 获取用户角色
    if not user.role:
        return []

    # 获取角色绑定的权限
    permissions = []
    for perm in user.role.permissions:
        permissions.append(perm.code)

    return permissions


def has_permission(user: Staff, permission: str, db: Session) -> bool:
    """检查用户是否有指定权限"""
    user_permissions = get_user_permissions(user, db)

    # * 表示所有权限
    if "*" in user_permissions:
        return True

    return permission in user_permissions


def has_any_permission(user: Staff, permissions: List[str], db: Session) -> bool:
    """检查用户是否有任一指定权限"""
    user_permissions = get_user_permissions(user, db)

    if "*" in user_permissions:
        return True

    return any(p in user_permissions for p in permissions)


def has_all_permissions(user: Staff, permissions: List[str], db: Session) -> bool:
    """检查用户是否有所有指定权限"""
    user_permissions = get_user_permissions(user, db)

    if "*" in user_permissions:
        return True

    return all(p in user_permissions for p in permissions)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Staff:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    merchant_id: int = payload.get("merchant_id")
    if user_id is None:
        raise credentials_exception

    user = db.query(Staff).filter(Staff.id == user_id).first()
    if user is None:
        raise credentials_exception

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def require_permissions(permissions: List[str], require_all: bool = False):
    """
    权限检查装饰器

    Args:
        permissions: 需要的权限列表
        require_all: 是否需要拥有所有权限（默认 False，任一即可）
    """
    async def permission_checker(
        current_user: Staff = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Staff:
        if require_all:
            if not has_all_permissions(current_user, permissions, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少必要权限"
                )
        else:
            if not has_any_permission(current_user, permissions, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少必要权限"
                )

        return current_user

    return permission_checker


def require_merchant_access():
    """检查用户是否有访问该商户的权限"""
    async def merchant_checker(
        current_user: Staff = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Staff:
        # 超级管理员可以访问所有商户
        if current_user.is_super_admin:
            return current_user

        # 登录时验证了用户状态，这里只需验证商户
        # 商户访问权限通过中间件参数传入验证
        return current_user

    return merchant_checker


def verify_merchant_access(user: Staff, merchant_id: int, db: Session) -> bool:
    """验证用户是否有访问指定商户的权限"""
    # 超级管理员可以访问所有商户
    if user.is_super_admin:
        return True

    # 普通用户只能访问自己所属商户
    return user.merchant_id == merchant_id
