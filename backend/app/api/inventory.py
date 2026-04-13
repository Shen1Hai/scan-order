from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.inventory import Inventory, InventoryLog
from app.models.staff import Staff
from app.schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    InventoryLogCreate, InventoryLogResponse
)
from app.services.websocket import notify_low_stock

router = APIRouter(prefix="/api/inventory", tags=["库存管理"])


@router.get("", response_model=List[InventoryResponse])
async def list_inventory(
    keyword: str = Query(None, description="关键词搜索"),
    is_low_stock: bool = Query(None, description="仅显示库存不足"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取库存列表"""
    query = db.query(Inventory)

    if keyword:
        query = query.filter(Inventory.name.like(f"%{keyword}%"))

    items = query.order_by(Inventory.id).all()

    # 检查库存是否不足
    result = []
    for item in items:
        item_dict = {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "low_stock_threshold": item.low_stock_threshold,
            "updated_at": item.updated_at,
            "is_low_stock": item.quantity <= item.low_stock_threshold
        }
        result.append(item_dict)

    if is_low_stock:
        result = [item for item in result if item["is_low_stock"]]

    return result


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取库存详情"""
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存不存在")

    return {
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "unit": item.unit,
        "low_stock_threshold": item.low_stock_threshold,
        "updated_at": item.updated_at,
        "is_low_stock": item.quantity <= item.low_stock_threshold
    }


@router.post("", response_model=InventoryResponse)
async def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["inventory:write"]))
):
    """创建库存物品"""
    item = Inventory(merchant_id=current_user.merchant_id, **inventory_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "unit": item.unit,
        "low_stock_threshold": item.low_stock_threshold,
        "updated_at": item.updated_at,
        "is_low_stock": item.quantity <= item.low_stock_threshold
    }


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["inventory:write"]))
):
    """更新库存物品"""
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存不存在")

    update_data = inventory_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "name": item.name,
        "quantity": item.quantity,
        "unit": item.unit,
        "low_stock_threshold": item.low_stock_threshold,
        "updated_at": item.updated_at,
        "is_low_stock": item.quantity <= item.low_stock_threshold
    }


@router.delete("/{inventory_id}")
async def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["inventory:write"]))
):
    """删除库存物品"""
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存不存在")

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{inventory_id}/logs", response_model=List[InventoryLogResponse])
async def get_inventory_logs(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取库存操作记录"""
    logs = db.query(InventoryLog) \
        .filter(InventoryLog.inventory_id == inventory_id) \
        .order_by(InventoryLog.created_at.desc()) \
        .all()

    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "inventory_id": log.inventory_id,
            "type": log.type,
            "quantity": log.quantity,
            "operator_id": log.operator_id,
            "operator_name": log.operator.name if log.operator else None,
            "note": log.note,
            "created_at": log.created_at
        })

    return result


@router.post("/{inventory_id}/log", response_model=InventoryLogResponse)
async def create_inventory_log(
    inventory_id: int,
    log_data: InventoryLogCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["inventory:log"]))
):
    """创建库存出入库记录"""
    item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存不存在")

    # 更新库存数量
    if log_data.type == "in":
        item.quantity += log_data.quantity
    elif log_data.type == "out":
        if item.quantity < log_data.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        item.quantity -= log_data.quantity
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")

    # 创建记录
    log = InventoryLog(
        inventory_id=inventory_id,
        type=log_data.type,
        quantity=log_data.quantity,
        operator_id=current_user.id,
        note=log_data.note
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # 检查是否库存不足，发送预警
    if item.quantity <= item.low_stock_threshold:
        notify_low_stock({
            "id": item.id,
            "name": item.name,
            "quantity": float(item.quantity),
            "unit": item.unit,
            "threshold": float(item.low_stock_threshold)
        })

    return {
        "id": log.id,
        "inventory_id": log.inventory_id,
        "type": log.type,
        "quantity": log.quantity,
        "operator_id": log.operator_id,
        "operator_name": current_user.name,
        "note": log.note,
        "created_at": log.created_at
    }
