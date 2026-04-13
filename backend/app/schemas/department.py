from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    """部门基础"""
    name: str = Field(..., max_length=50, description="部门名称")
    code: str = Field(..., max_length=50, description="部门编码")
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    sort_order: int = Field(0, description="排序")
    status: str = Field("active", description="状态: active/inactive")


class DepartmentCreate(DepartmentBase):
    """创建部门"""
    manager_id: Optional[int] = Field(None, description="部门负责人ID")


class DepartmentUpdate(BaseModel):
    """更新部门"""
    name: Optional[str] = Field(None, max_length=50, description="部门名称")
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[str] = Field(None, description="状态: active/inactive")


class DepartmentResponse(DepartmentBase):
    """部门响应"""
    id: int
    merchant_id: int
    manager_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentWithChildren(DepartmentResponse):
    """带子部门的部门"""
    children: List["DepartmentWithChildren"] = []
    manager_name: Optional[str] = None

    class Config:
        from_attributes = True


# 解决循环引用
DepartmentWithChildren.model_rebuild()
