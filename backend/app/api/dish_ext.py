from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.staff import Staff
from app.models.dish import Dish
from app.models.dish_spec import DishSpec
from app.models.dish_cooking import DishCooking
from app.schemas.dish_ext import (
    DishSpecCreate, DishSpecUpdate, DishSpecResponse,
    DishCookingCreate, DishCookingUpdate, DishCookingResponse
)

router = APIRouter(prefix="/api/dishes", tags=["菜品规格和做法"])


# ============ 菜品规格 ============

@router.get("/{dish_id}/specs", response_model=List[DishSpecResponse])
async def list_dish_specs(dish_id: int, db: Session = Depends(get_db)):
    """获取菜品的所有规格"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    specs = db.query(DishSpec).filter(DishSpec.dish_id == dish_id).order_by(DishSpec.sort_order).all()
    return specs


@router.post("/{dish_id}/specs", response_model=DishSpecResponse)
async def create_dish_spec(
    dish_id: int,
    spec_data: DishSpecCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """为菜品添加规格"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    # 如果设置为默认，取消其他默认
    if spec_data.is_default:
        db.query(DishSpec).filter(DishSpec.dish_id == dish_id).update({"is_default": False})

    spec = DishSpec(dish_id=dish_id, **spec_data.model_dump())
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


@router.put("/specs/{spec_id}", response_model=DishSpecResponse)
async def update_dish_spec(
    spec_id: int,
    spec_data: DishSpecUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """更新规格"""
    spec = db.query(DishSpec).filter(DishSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="规格不存在")

    update_data = spec_data.model_dump(exclude_unset=True)

    # 如果设置为默认，取消其他默认
    if update_data.get("is_default"):
        db.query(DishSpec).filter(
            DishSpec.dish_id == spec.dish_id,
            DishSpec.id != spec_id
        ).update({"is_default": False})

    for key, value in update_data.items():
        setattr(spec, key, value)

    db.commit()
    db.refresh(spec)
    return spec


@router.delete("/specs/{spec_id}")
async def delete_dish_spec(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """删除规格"""
    spec = db.query(DishSpec).filter(DishSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="规格不存在")

    db.delete(spec)
    db.commit()
    return {"message": "删除成功"}


# ============ 菜品做法 ============

@router.get("/cookings", response_model=List[DishCookingResponse])
async def list_cookings(
    status: str = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """获取所有做法列表"""
    query = db.query(DishCooking)
    if status:
        query = query.filter(DishCooking.status == status)
    return query.order_by(DishCooking.sort_order).all()


@router.post("/cookings", response_model=DishCookingResponse)
async def create_cooking(
    cooking_data: DishCookingCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """创建做法"""
    # 检查名称是否已存在
    existing = db.query(DishCooking).filter(DishCooking.name == cooking_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="做法名称已存在")

    cooking = DishCooking(**cooking_data.model_dump())
    db.add(cooking)
    db.commit()
    db.refresh(cooking)
    return cooking


@router.put("/cookings/{cooking_id}", response_model=DishCookingResponse)
async def update_cooking(
    cooking_id: int,
    cooking_data: DishCookingUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """更新做法"""
    cooking = db.query(DishCooking).filter(DishCooking.id == cooking_id).first()
    if not cooking:
        raise HTTPException(status_code=404, detail="做法不存在")

    update_data = cooking_data.model_dump(exclude_unset=True)

    # 检查名称冲突
    if update_data.get("name"):
        existing = db.query(DishCooking).filter(
            DishCooking.name == update_data["name"],
            DishCooking.id != cooking_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="做法名称已存在")

    for key, value in update_data.items():
        setattr(cooking, key, value)

    db.commit()
    db.refresh(cooking)
    return cooking


@router.delete("/cookings/{cooking_id}")
async def delete_cooking(
    cooking_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """删除做法"""
    cooking = db.query(DishCooking).filter(DishCooking.id == cooking_id).first()
    if not cooking:
        raise HTTPException(status_code=404, detail="做法不存在")

    db.delete(cooking)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{dish_id}/cookings")
async def set_dish_cookings(
    dish_id: int,
    cooking_ids: List[int],
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """设置菜品的做法"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    # 获取做法
    cookings = db.query(DishCooking).filter(DishCooking.id.in_(cooking_ids)).all()
    dish.cooking_methods = cookings

    db.commit()
    return {"message": "设置成功", "cookings": [c.id for c in cookings]}
