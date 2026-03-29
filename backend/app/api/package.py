from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.staff import Staff
from app.models.dish import Dish
from app.models.package import DishPackage, PackageItem
from app.schemas.dish_ext import (
    DishPackageCreate, DishPackageUpdate, DishPackageResponse,
    PackageItemResponse
)

router = APIRouter(prefix="/api/packages", tags=["套餐管理"])


@router.get("", response_model=List[DishPackageResponse])
async def list_packages(
    status: str = Query(None, description="状态筛选"),
    is_recommended: bool = Query(None, description="仅推荐"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取套餐列表"""
    query = db.query(DishPackage).options(joinedload(DishPackage.items))

    if status:
        query = query.filter(DishPackage.status == status)
    if is_recommended:
        query = query.filter(DishPackage.is_recommended == True)

    packages = query.order_by(DishPackage.id.desc()).all()
    return packages


@router.get("/{package_id}", response_model=DishPackageResponse)
async def get_package(package_id: int, db: Session = Depends(get_db)):
    """获取套餐详情"""
    package = db.query(DishPackage).options(
        joinedload(DishPackage.items)
    ).filter(DishPackage.id == package_id).first()

    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    return package


@router.post("", response_model=DishPackageResponse)
async def create_package(
    package_data: DishPackageCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """创建套餐"""
    merchant_id = current_user.merchant_id if not current_user.is_super_admin else 1

    # 创建套餐
    package = DishPackage(
        merchant_id=merchant_id,
        name=package_data.name,
        description=package_data.description,
        image=package_data.image,
        price=package_data.price,
        original_price=package_data.original_price,
        stock=package_data.stock,
        is_recommended=package_data.is_recommended
    )
    db.add(package)
    db.flush()

    # 添加套餐项
    for item_data in package_data.items:
        item = PackageItem(
            package_id=package.id,
            dish_id=item_data.dish_id,
            dish_name=item_data.dish_name,
            quantity=item_data.quantity,
            price=item_data.price
        )
        db.add(item)

    db.commit()
    db.refresh(package)

    return package


@router.put("/{package_id}", response_model=DishPackageResponse)
async def update_package(
    package_id: int,
    package_data: DishPackageUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """更新套餐"""
    package = db.query(DishPackage).filter(DishPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    update_data = package_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(package, key, value)

    db.commit()
    db.refresh(package)
    return package


@router.delete("/{package_id}")
async def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """删除套餐"""
    package = db.query(DishPackage).filter(DishPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    db.delete(package)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{package_id}/items")
async def add_package_item(
    package_id: int,
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """添加套餐项"""
    package = db.query(DishPackage).filter(DishPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="套餐不存在")

    # 如果传了 dish_id，获取菜品信息
    dish_name = item_data.get("dish_name", "")
    price = item_data.get("price", 0)

    if item_data.get("dish_id"):
        dish = db.query(Dish).filter(Dish.id == item_data["dish_id"]).first()
        if dish:
            dish_name = dish.name
            price = float(dish.price)

    item = PackageItem(
        package_id=package_id,
        dish_id=item_data.get("dish_id"),
        dish_name=dish_name,
        quantity=item_data.get("quantity", 1),
        price=price
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.delete("/{package_id}/items/{item_id}")
async def delete_package_item(
    package_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["dish:write"]))
):
    """删除套餐项"""
    item = db.query(PackageItem).filter(
        PackageItem.id == item_id,
        PackageItem.package_id == package_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="套餐项不存在")

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}
