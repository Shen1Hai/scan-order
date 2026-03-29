from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class DishBase(BaseModel):
    """菜品基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="菜品名称")
    category_id: Optional[int] = Field(None, description="分类ID")
    price: Decimal = Field(..., gt=0, description="价格")
    description: Optional[str] = Field(None, description="描述")
    image: Optional[str] = Field(None, description="图片URL")
    stock: int = Field(default=0, ge=0, description="库存")
    status: str = Field(default="active", description="状态: active/off_sale")


class DishCreate(DishBase):
    """创建菜品请求"""
    pass


class DishUpdate(BaseModel):
    """更新菜品请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="菜品名称")
    category_id: Optional[int] = Field(None, description="分类ID")
    price: Optional[Decimal] = Field(None, gt=0, description="价格")
    description: Optional[str] = Field(None, description="描述")
    image: Optional[str] = Field(None, description="图片URL")
    stock: Optional[int] = Field(None, ge=0, description="库存")
    status: Optional[str] = Field(None, description="状态")


class DishResponse(DishBase):
    """菜品响应"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DishWithCategory(DishResponse):
    """带分类信息的菜品响应"""
    category_name: Optional[str] = None
