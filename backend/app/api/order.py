from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.order import Order, OrderItem
from app.models.table import Table
from app.models.dish import Dish
from app.models.staff import Staff
from app.schemas.order import (
    OrderCreate, OrderStatusUpdate, OrderResponse,
    OrderDetailResponse, OrderListResponse
)
from app.services.websocket import notify_new_order

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = str(uuid.uuid4())[:4].upper()
    return f"ORD{timestamp}{random_str}"


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    status: str = Query(None, description="状态筛选"),
    table_id: int = Query(None, description="桌位ID筛选"),
    start_date: str = Query(None, description="开始日期"),
    end_date: str = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取订单列表"""
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)
    if table_id:
        query = query.filter(Order.table_id == table_id)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return orders


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return order


@router.get("/no/{order_no}", response_model=OrderDetailResponse)
async def get_order_by_no(order_no: str, db: Session = Depends(get_db)):
    """通过订单号获取订单"""
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return order


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """创建订单（顾客点单）"""
    # 验证桌位存在
    table = db.query(Table).filter(Table.id == order_data.table_id).first()
    if not table:
        raise HTTPException(status_code=400, detail="桌位不存在")

    # 计算总金额
    total_amount = Decimal("0")
    order_items = []

    for item in order_data.items:
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=400, detail=f"菜品ID {item.dish_id} 不存在")
        if dish.status != "active":
            raise HTTPException(status_code=400, detail=f"菜品 {dish.name} 已下架")

        item_total = dish.price * item.quantity
        total_amount += item_total
        order_items.append({
            "dish_id": dish.id,
            "dish_name": dish.name,
            "price": dish.price,
            "quantity": item.quantity
        })

    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        table_id=table.id,
        table_name=table.name,
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    db.flush()

    # 创建订单项
    for item_data in order_items:
        order_item = OrderItem(order_id=order.id, **item_data)
        db.add(order_item)

    # 更新桌位状态
    table.status = "occupied"

    db.commit()
    db.refresh(order)

    # WebSocket 通知后台有新订单
    notify_new_order(order)

    return order


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """模拟支付"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不允许支付")

    order.status = "paid"
    order.pay_time = datetime.now()

    db.commit()
    db.refresh(order)

    return {"message": "支付成功", "order_no": order.order_no}


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin", "cashier", "cook"]))
):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证状态转换
    valid_transitions = {
        "pending": ["paid", "cancelled"],
        "paid": ["preparing", "cancelled"],
        "preparing": ["ready"],
        "ready": ["completed"],
        "completed": [],
        "cancelled": []
    }

    if status_data.status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"不允许从 {order.status} 直接转换为 {status_data.status}"
        )

    order.status = status_data.status

    # 如果是完成或取消，释放桌位
    if status_data.status in ["completed", "cancelled"]:
        table = db.query(Table).filter(Table.id == order.table_id).first()
        if table:
            table.status = "idle"

    db.commit()
    db.refresh(order)

    return order


@router.delete("/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin", "cashier"]))
):
    """取消订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status not in ["pending", "paid"]:
        raise HTTPException(status_code=400, detail="当前状态不允许取消")

    order.status = "cancelled"

    # 释放桌位
    if order.table_id:
        table = db.query(Table).filter(Table.id == order.table_id).first()
        if table:
            table.status = "idle"

    db.commit()
    return {"message": "订单已取消"}
