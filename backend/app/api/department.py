from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.department import Department
from app.models.staff import Staff
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentWithChildren
)

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


def build_department_tree(departments: List[Department], parent_id=None) -> List[dict]:
    """构建部门树"""
    tree = []
    for dept in departments:
        if dept.parent_id == parent_id:
            dept_dict = {
                "id": dept.id,
                "merchant_id": dept.merchant_id,
                "name": dept.name,
                "code": dept.code,
                "parent_id": dept.parent_id,
                "sort_order": dept.sort_order,
                "status": dept.status,
                "manager_id": dept.manager_id,
                "manager_name": dept.manager.name if dept.manager else None,
                "created_at": dept.created_at.isoformat() if dept.created_at else None,
                "children": build_department_tree(departments, dept.id)
            }
            tree.append(dept_dict)
    return tree


@router.get("", response_model=List[DepartmentResponse])
async def list_departments(
    parent_id: int = Query(None, description="上级部门ID，null表示顶级部门"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取部门列表"""
    query = db.query(Department).filter(Department.merchant_id == current_user.merchant_id)
    if parent_id is not None:
        query = query.filter(Department.parent_id == parent_id)
    else:
        query = query.filter(Department.parent_id == None)
    return query.order_by(Department.sort_order, Department.id).all()


@router.get("/tree", response_model=List[dict])
async def get_department_tree(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取部门树（完整结构）"""
    departments = db.query(Department).filter(
        Department.merchant_id == current_user.merchant_id
    ).order_by(Department.sort_order, Department.id).all()
    return build_department_tree(departments, parent_id=None)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取部门详情"""
    dept = db.query(Department).filter(
        Department.id == department_id,
        Department.merchant_id == current_user.merchant_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept


@router.post("", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["department:write"]))
):
    """创建部门"""
    # 检查编码唯一性
    existing = db.query(Department).filter(
        Department.merchant_id == current_user.merchant_id,
        Department.code == dept_data.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="部门编码已存在")

    # 验证上级部门存在
    if dept_data.parent_id:
        parent = db.query(Department).filter(
            Department.id == dept_data.parent_id,
            Department.merchant_id == current_user.merchant_id
        ).first()
        if not parent:
            raise HTTPException(status_code=400, detail="上级部门不存在")

    dept = Department(
        merchant_id=current_user.merchant_id,
        name=dept_data.name,
        code=dept_data.code,
        parent_id=dept_data.parent_id,
        sort_order=dept_data.sort_order,
        status=dept_data.status,
        manager_id=dept_data.manager_id
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    dept_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["department:write"]))
):
    """更新部门"""
    dept = db.query(Department).filter(
        Department.id == department_id,
        Department.merchant_id == current_user.merchant_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    update_dict = dept_data.model_dump(exclude_unset=True)

    # 验证上级部门
    if 'parent_id' in update_dict and update_dict['parent_id']:
        # 不能把自己设为上级
        if update_dict['parent_id'] == department_id:
            raise HTTPException(status_code=400, detail="不能将自己设为上级部门")
        parent = db.query(Department).filter(
            Department.id == update_dict['parent_id'],
            Department.merchant_id == current_user.merchant_id
        ).first()
        if not parent:
            raise HTTPException(status_code=400, detail="上级部门不存在")

    for key, value in update_dict.items():
        setattr(dept, key, value)

    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["department:write"]))
):
    """删除部门（如果有子部门或员工则不能删除）"""
    dept = db.query(Department).filter(
        Department.id == department_id,
        Department.merchant_id == current_user.merchant_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    # 检查是否有子部门
    children = db.query(Department).filter(Department.parent_id == department_id).first()
    if children:
        raise HTTPException(status_code=400, detail="请先删除子部门")

    # 检查是否有员工
    if dept.staff:
        raise HTTPException(status_code=400, detail="请先移除部门员工")

    db.delete(dept)
    db.commit()
    return {"message": "删除成功"}


@router.put("/{department_id}/manager")
async def set_department_manager(
    department_id: int,
    manager_id: int = Query(..., description="部门负责人ID"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["department:write"]))
):
    """设置部门负责人"""
    dept = db.query(Department).filter(
        Department.id == department_id,
        Department.merchant_id == current_user.merchant_id
    ).first()
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")

    # 验证员工存在且属于同一商户
    staff = db.query(Staff).filter(
        Staff.id == manager_id,
        Staff.merchant_id == current_user.merchant_id
    ).first()
    if not staff:
        raise HTTPException(status_code=400, detail="员工不存在")

    dept.manager_id = manager_id
    db.commit()
    return {"message": "设置成功"}
