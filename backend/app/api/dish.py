from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.dish import Dish
from app.models.category import Category
from app.models.staff import Staff
from app.schemas.dish import DishCreate, DishUpdate, DishResponse, DishWithCategory

router = APIRouter(prefix="/api/dishes", tags=["菜品管理"])


@router.get("", response_model=List[DishWithCategory])
async def list_dishes(
    category_id: int = Query(None, description="分类ID筛选"),
    status: str = Query(None, description="状态筛选"),
    keyword: str = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db)
):
    """获取菜品列表"""
    query = db.query(Dish).options(joinedload(Dish.category))

    if category_id:
        query = query.filter(Dish.category_id == category_id)
    if status:
        query = query.filter(Dish.status == status)
    if keyword:
        query = query.filter(Dish.name.like(f"%{keyword}%"))

    dishes = query.order_by(Dish.category_id, Dish.id).all()

    # 转换结果，添加分类名称
    result = []
    for dish in dishes:
        dish_dict = {
            "id": dish.id,
            "category_id": dish.category_id,
            "name": dish.name,
            "price": dish.price,
            "description": dish.description,
            "image": dish.image,
            "status": dish.status,
            "stock": dish.stock,
            "created_at": dish.created_at,
            "category_name": dish.category.name if dish.category else None
        }
        result.append(dish_dict)

    return result


@router.get("/{dish_id}", response_model=DishWithCategory)
async def get_dish(dish_id: int, db: Session = Depends(get_db)):
    """获取菜品详情"""
    dish = db.query(Dish).options(joinedload(Dish.category)).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    return {
        "id": dish.id,
        "category_id": dish.category_id,
        "name": dish.name,
        "price": dish.price,
        "description": dish.description,
        "image": dish.image,
        "status": dish.status,
        "stock": dish.stock,
        "created_at": dish.created_at,
        "category_name": dish.category.name if dish.category else None
    }


@router.post("", response_model=DishResponse)
async def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin", "cashier"]))
):
    """创建菜品"""
    # 验证分类存在
    if dish_data.category_id:
        category = db.query(Category).filter(Category.id == dish_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")

    dish = Dish(**dish_data.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


@router.put("/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin", "cashier"]))
):
    """更新菜品"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    update_data = dish_data.model_dump(exclude_unset=True)

    # 验证分类
    if update_data.get("category_id"):
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")

    for key, value in update_data.items():
        setattr(dish, key, value)

    db.commit()
    db.refresh(dish)
    return dish


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
):
    """删除菜品（仅管理员）"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")

    db.delete(dish)
    db.commit()
    return {"message": "删除成功"}
