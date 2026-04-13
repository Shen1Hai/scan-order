from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StaffBase(BaseModel):
    """员工基础Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    role_id: Optional[int] = Field(None, description="角色ID")
    role: Optional[str] = Field(None, description="角色代码")


class StaffCreate(StaffBase):
    """创建员工请求"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class StaffUpdate(BaseModel):
    """更新员工请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="姓名")
    role_id: Optional[int] = Field(None, description="角色ID")
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码")


class StaffResponse(BaseModel):
    """员工响应"""
    id: int
    username: str
    name: str
    role: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token载荷数据"""
    user_id: Optional[int] = None
