from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, create_access_token,
    get_current_user, get_user_permissions
)
from app.core.config import settings
from app.models.staff import Staff
from app.models.merchant import Merchant
from app.schemas.staff import (
    LoginRequest, Token, StaffCreate, StaffResponse, StaffUpdate
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    员工登录
    支持用户名格式: username 或 username@merchant_code
    """
    username = login_data.username
    merchant_code = None

    # 支持 username@merchant_code 格式
    if "@" in username:
        parts = username.split("@", 1)
        username = parts[0]
        merchant_code = parts[1]

    # 查找用户
    if merchant_code:
        # 指定商户登录
        merchant = db.query(Merchant).filter(Merchant.code == merchant_code).first()
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="商户不存在"
            )
        user = db.query(Staff).filter(
            Staff.merchant_id == merchant.id,
            Staff.username == username
        ).first()
    else:
        # 默认查找超级管理员或第一个匹配用户
        user = db.query(Staff).filter(Staff.username == username).first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建 Token，包含用户ID和商户ID
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "merchant_id": user.merchant_id,
            "role": user.role.code if user.role else None
        }
    )

    return Token(access_token=access_token)


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """表单登录（支持 OAuth2PasswordBearer）"""
    username = form_data.username
    merchant_code = None

    if "@" in username:
        parts = username.split("@", 1)
        username = parts[0]
        merchant_code = parts[1]

    if merchant_code:
        merchant = db.query(Merchant).filter(Merchant.code == merchant_code).first()
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="商户不存在"
            )
        user = db.query(Staff).filter(
            Staff.merchant_id == merchant.id,
            Staff.username == username
        ).first()
    else:
        user = db.query(Staff).filter(Staff.username == username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    access_token = create_access_token(
        data={
            "sub": user.id,
            "merchant_id": user.merchant_id,
            "role": user.role.code if user.role else None
        }
    )

    return Token(access_token=access_token)


@router.get("/profile", response_model=StaffResponse)
async def get_profile(
    current_user: Staff = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "role": current_user.role.code if current_user.role else None,
        "created_at": current_user.created_at
    }


@router.get("/permissions")
async def get_my_permissions(
    current_user: Staff = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的权限列表"""
    permissions = get_user_permissions(current_user, db)
    return {"permissions": permissions}


@router.get("/merchants")
async def get_accessible_merchants(
    current_user: Staff = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户可访问的商户列表"""
    if current_user.is_super_admin:
        # 超级管理员可访问所有商户
        merchants = db.query(Merchant).filter(Merchant.status == "active").all()
    else:
        # 普通用户只能访问所属商户
        merchants = [current_user.merchant]

    return {
        "merchants": [
            {
                "id": m.id,
                "name": m.name,
                "code": m.code,
                "level": m.level
            }
            for m in merchants
        ]
    }


@router.post("/register", response_model=StaffResponse)
async def register(
    staff_data: StaffCreate,
    merchant_id: int = Query(..., description="商户ID"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """注册新员工（需要商户管理权限）"""
    from app.core.security import has_any_permission

    # 验证权限
    if not current_user.is_super_admin:
        if not has_any_permission(current_user, ["staff:write"], db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有员工管理权限"
            )

    # 验证商户
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="商户不存在")

    # 验证访问权限
    if not current_user.is_super_admin and current_user.merchant_id != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法为其他商户创建员工"
        )

    # 检查用户名是否已存在（同一商户下唯一）
    existing = db.query(Staff).filter(
        Staff.merchant_id == merchant_id,
        Staff.username == staff_data.username
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建员工
    from app.core.security import get_password_hash
    new_staff = Staff(
        merchant_id=merchant_id,
        username=staff_data.username,
        password=get_password_hash(staff_data.password),
        name=staff_data.name,
        role_id=staff_data.role_id if hasattr(staff_data, 'role_id') else None
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return {
        "id": new_staff.id,
        "username": new_staff.username,
        "name": new_staff.name,
        "role": new_staff.role.code if new_staff.role else None,
        "created_at": new_staff.created_at
    }
