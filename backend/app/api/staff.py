from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_roles, get_password_hash
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse

router = APIRouter(prefix="/api/staff", tags=["员工管理"])


@router.get("", response_model=List[StaffResponse])
async def list_staff(
    role: str = Query(None, description="角色筛选"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
):
    """获取员工列表（仅管理员）"""
    query = db.query(Staff)
    if role:
        query = query.filter(Staff.role == role)
    return query.order_by(Staff.id).all()


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
):
    """获取员工详情"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="员工不存在")
    return staff


@router.post("", response_model=StaffResponse)
async def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
):
    """创建员工"""
    # 检查用户名是否已存在
    existing = db.query(Staff).filter(Staff.username == staff_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    staff = Staff(
        username=staff_data.username,
        password=get_password_hash(staff_data.password),
        name=staff_data.name,
        role=staff_data.role
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
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
    return staff


@router.delete("/{staff_id}")
async def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
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
