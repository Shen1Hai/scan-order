from pydantic import BaseModel, Field
from typing import List, Optional


class PermissionInfo(BaseModel):
    """权限信息"""
    id: int
    code: str
    name: str
    category: str

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基础"""
    code: str = Field(..., max_length=50, description="角色编码")
    name: str = Field(..., max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色"""
    permission_ids: List[int] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = Field(None, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")
    permission_ids: Optional[List[int]] = Field(None, description="权限ID列表")


class RoleResponse(RoleBase):
    """角色响应"""
    id: int
    is_system: bool
    permissions: List[PermissionInfo] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    """更新角色权限"""
    permission_ids: List[int] = Field(..., description="权限ID列表")
