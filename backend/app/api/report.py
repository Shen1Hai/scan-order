from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.order import Order, OrderItem
from app.models.staff import Staff
from app.models.dish import Dish

router = APIRouter(prefix="/api/reports", tags=["报表统计"])


@router.get("/sales")
async def get_sales_report(
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取销售统计"""
    # 默认今天
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # 总销售额
    total_query = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(["paid", "preparing", "ready", "completed"]),
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    )
    total_sales = total_query.scalar() or Decimal("0")

    # 订单数
    order_count = db.query(func.count(Order.id)).filter(
        Order.status != "cancelled",
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).scalar()

    # 已完成订单数
    completed_count = db.query(func.count(Order.id)).filter(
        Order.status == "completed",
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).scalar()

    # 取消订单数
    cancelled_count = db.query(func.count(Order.id)).filter(
        Order.status == "cancelled",
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).scalar()

    # 每日销售额趋势
    daily_sales = db.query(
        func.date(Order.created_at).label("date"),
        func.sum(Order.total_amount).label("amount"),
        func.count(Order.id).label("count")
    ).filter(
        Order.status.in_(["paid", "preparing", "ready", "completed"]),
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()

    return {
        "total_sales": float(total_sales),
        "order_count": order_count,
        "completed_count": completed_count,
        "cancelled_count": cancelled_count,
        "average_order_value": float(total_sales / order_count) if order_count > 0 else 0,
        "daily_sales": [
            {
                "date": str(item.date),
                "amount": float(item.amount),
                "count": item.count
            }
            for item in daily_sales
        ]
    }


@router.get("/dishes")
async def get_dish_sales_report(
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取菜品销量排行"""
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # 按菜品分组统计
    dish_sales = db.query(
        OrderItem.dish_id,
        OrderItem.dish_name,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.price * OrderItem.quantity).label("total_amount")
    ).join(Order).filter(
        Order.status.in_(["paid", "preparing", "ready", "completed"]),
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).group_by(
        OrderItem.dish_id, OrderItem.dish_name
    ).order_by(func.sum(OrderItem.quantity).desc()).limit(limit).all()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "dishes": [
            {
                "dish_id": item.dish_id,
                "dish_name": item.dish_name,
                "total_quantity": item.total_quantity,
                "total_amount": float(item.total_amount)
            }
            for item in dish_sales
        ]
    }


@router.get("/staff")
async def get_staff_report(
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_roles(["admin"]))
):
    """获取员工业绩统计"""
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # 统计每个员工处理的订单
    # 注意: 这里按最后更新订单的员工来统计（简化版）
    # 实际生产可能需要记录每个操作员
    staff_orders = db.query(
        Staff.id,
        Staff.name,
        Staff.role,
        func.count(Order.id).label("order_count"),
        func.sum(Order.total_amount).label("total_amount")
    ).outerjoin(Order, Staff.id == Order.table_id).filter(
        Order.status != "cancelled",
        Order.created_at >= start_date,
        Order.created_at <= end_date + " 23:59:59"
    ).group_by(Staff.id, Staff.name, Staff.role).all()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "staff": [
            {
                "staff_id": item.id,
                "name": item.name,
                "role": item.role,
                "order_count": item.order_count or 0,
                "total_amount": float(item.total_amount or 0)
            }
            for item in staff_orders
        ]
    }


@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取仪表盘数据"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 今日销售额
    today_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(["paid", "preparing", "ready", "completed"]),
        func.date(Order.created_at) == today
    ).scalar() or Decimal("0")

    # 今日订单数
    today_orders = db.query(func.count(Order.id)).filter(
        Order.status != "cancelled",
        func.date(Order.created_at) == today
    ).scalar()

    # 待处理订单数
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status.in_(["pending", "paid", "preparing"])
    ).scalar()

    # 畅销菜品 (今日)
    top_dishes = db.query(
        OrderItem.dish_name,
        func.sum(OrderItem.quantity).label("total_quantity")
    ).join(Order).filter(
        Order.status.in_(["paid", "preparing", "ready", "completed"]),
        func.date(Order.created_at) == today
    ).group_by(OrderItem.dish_name).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

    return {
        "today_sales": float(today_sales),
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "top_dishes": [
            {"name": item.dish_name, "quantity": item.total_quantity}
            for item in top_dishes
        ]
    }
