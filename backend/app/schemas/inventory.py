from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InventoryBase(BaseModel):
    """库存基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="物品名称")
    quantity: Decimal = Field(default=0, description="数量")
    unit: str = Field(default="个", description="单位")
    low_stock_threshold: Decimal = Field(default=10, description="库存预警阈值")


class InventoryCreate(InventoryBase):
    """创建库存请求"""
    pass


class InventoryUpdate(BaseModel):
    """更新库存请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="物品名称")
    quantity: Optional[Decimal] = Field(None, description="数量")
    unit: Optional[str] = Field(None, description="单位")
    low_stock_threshold: Optional[Decimal] = Field(None, description="库存预警阈值")


class InventoryResponse(InventoryBase):
    """库存响应"""
    id: int
    updated_at: Optional[datetime] = None
    is_low_stock: bool = False  # 是否库存不足

    class Config:
        from_attributes = True


class InventoryLogBase(BaseModel):
    """库存记录基础Schema"""
    type: str = Field(..., description="类型: in/out")
    quantity: Decimal = Field(..., gt=0, description="数量")
    note: Optional[str] = Field(None, description="备注")


class InventoryLogCreate(InventoryLogBase):
    """创建库存记录请求"""
    pass


class InventoryLogResponse(InventoryLogBase):
    """库存记录响应"""
    id: int
    inventory_id: int
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
