from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    sort_order: int = Field(default=0, description="排序顺序")
    status: str = Field(default="active", description="状态: active/inactive")


class CategoryCreate(CategoryBase):
    """创建分类请求"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    status: Optional[str] = Field(None, description="状态")


class CategoryResponse(CategoryBase):
    """分类响应"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
