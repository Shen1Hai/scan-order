from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItemBase(BaseModel):
    """订单项基础Schema"""
    dish_id: int = Field(..., description="菜品ID")
    dish_name: str = Field(..., description="菜品名称")
    price: Decimal = Field(..., gt=0, description="单价")
    quantity: int = Field(default=1, ge=1, description="数量")


class OrderItemCreate(OrderItemBase):
    """创建订单项请求"""
    pass


class OrderItemResponse(OrderItemBase):
    """订单项响应"""
    id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """订单基础Schema"""
    table_id: int = Field(..., description="桌位ID")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="订单项列表")


class OrderCreate(OrderBase):
    """创建订单请求"""
    pass


class OrderStatusUpdate(BaseModel):
    """更新订单状态请求"""
    status: str = Field(..., description="状态: pending/paid/preparing/ready/completed/cancelled")


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_no: str
    table_id: Optional[int] = None
    table_name: Optional[str] = None
    total_amount: Decimal
    status: str
    pay_time: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """订单详情响应"""
    items: List[OrderItemResponse] = []


class OrderListResponse(BaseModel):
    """订单列表响应"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
