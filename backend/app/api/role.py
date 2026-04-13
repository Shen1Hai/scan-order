from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.permission import Role, Permission
from app.models.staff import Staff
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RolePermissionUpdate, PermissionInfo
)

router = APIRouter(prefix="/api/roles", tags=["角色管理"])


@router.get("/permissions", response_model=List[PermissionInfo])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取所有权限列表（用于分配）"""
    permissions = db.query(Permission).order_by(Permission.category, Permission.id).all()
    return permissions


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:read"]))
):
    """获取角色列表"""
    roles = db.query(Role).filter(Role.merchant_id == current_user.merchant_id).all()

    # 手动转换为 dict 确保正确序列化
    result = []
    for role in roles:
        role_dict = {
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "description": role.description,
            "is_system": role.is_system,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "permissions": [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "category": p.category
                }
                for p in role.permissions
            ]
        }
        result.append(role_dict)

    return result


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:read"]))
):
    """获取角色详情"""
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.merchant_id == current_user.merchant_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


@router.post("", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:write"]))
):
    """创建角色"""
    # 检查编码是否已存在
    existing = db.query(Role).filter(
        Role.merchant_id == current_user.merchant_id,
        Role.code == role_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色编码已存在")

    # 获取权限
    permissions = []
    if role_data.permission_ids:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()

    role = Role(
        merchant_id=current_user.merchant_id,
        code=role_data.code,
        name=role_data.name,
        description=role_data.description,
        permissions=permissions
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:write"]))
):
    """更新角色"""
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.merchant_id == current_user.merchant_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统内置角色不能修改")

    # 更新基本信息
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description

    # 更新权限
    if role_data.permission_ids is not None:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_data.permission_ids)
        ).all()
        role.permissions = permissions

    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:write"]))
):
    """删除角色"""
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.merchant_id == current_user.merchant_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统内置角色不能删除")

    # 检查是否有员工使用此角色
    if role.staff:
        raise HTTPException(status_code=400, detail="有员工使用此角色，无法删除")

    db.delete(role)
    db.commit()
    return {"message": "删除成功"}


@router.put("/{role_id}/permissions", response_model=RoleResponse)
async def update_role_permissions(
    role_id: int,
    perm_data: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["role:write"]))
):
    """更新角色权限"""
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.merchant_id == current_user.merchant_id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role.is_system:
        raise HTTPException(status_code=400, detail="系统内置角色不能修改权限")

    permissions = db.query(Permission).filter(
        Permission.id.in_(perm_data.permission_ids)
    ).all()
    role.permissions = permissions

    db.commit()
    db.refresh(role)
    return role
