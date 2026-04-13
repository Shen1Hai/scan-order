from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions, get_password_hash
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse

router = APIRouter(prefix="/api/staff", tags=["员工管理"])


@router.get("", response_model=List[StaffResponse])
async def list_staff(
    role: str = Query(None, description="角色筛选"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["staff:read"]))
):
    """获取员工列表（仅同一商户）"""
    query = db.query(Staff).filter(Staff.merchant_id == current_user.merchant_id)

    # 非超级管理员看不到超级管理员
    if not current_user.is_super_admin:
        query = query.filter(Staff.is_super_admin == False)
    if role:
        query = query.filter(Staff.role == role)
    staff_list = query.order_by(Staff.id).all()
    return [
        StaffResponse(
            id=s.id,
            username=s.username,
            name=s.name,
            role=s.role.code if s.role else None,
            created_at=s.created_at
        )
        for s in staff_list
    ]


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["staff:read"]))
):
    """获取员工详情"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    return StaffResponse(
        id=staff.id,
        username=staff.username,
        name=staff.name,
        role=staff.role.code if staff.role else None,
        created_at=staff.created_at
    )


@router.post("", response_model=StaffResponse)
async def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["staff:write"]))
):
    """创建员工"""
    # 检查用户名是否已存在
    existing = db.query(Staff).filter(Staff.username == staff_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 如果传了 role 代码而不是 role_id，需要查询角色ID
    role_id = staff_data.role_id
    if role_id is None and staff_data.role:
        from app.models.permission import Role
        role = db.query(Role).filter(
            Role.merchant_id == current_user.merchant_id,
            Role.code == staff_data.role
        ).first()
        if role:
            role_id = role.id

    staff = Staff(
        merchant_id=current_user.merchant_id,
        username=staff_data.username,
        password=get_password_hash(staff_data.password),
        name=staff_data.name,
        role_id=role_id
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return StaffResponse(
        id=staff.id,
        username=staff.username,
        name=staff.name,
        role=staff.role.code if staff.role else None,
        created_at=staff.created_at
    )


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["staff:write"]))
):
    """更新员工"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")

    update_data = staff_data.model_dump(exclude_unset=True)

    # 如果更新密码
    if update_data.get("password"):
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return StaffResponse(
        id=staff.id,
        username=staff.username,
        name=staff.name,
        role=staff.role.code if staff.role else None,
        created_at=staff.created_at
    )


@router.delete("/{staff_id}")
async def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["staff:write"]))
):
    """删除员工"""
    if staff_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")

    db.delete(staff)
    db.commit()
    return {"message": "删除成功"}
