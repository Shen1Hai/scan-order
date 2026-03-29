from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TableBase(BaseModel):
    """桌位基础Schema"""
    code: str = Field(..., min_length=1, max_length=20, description="桌位编码(二维码)")
    name: str = Field(..., min_length=1, max_length=50, description="桌位名称")
    status: str = Field(default="idle", description="状态: idle/occupied/reserved")


class TableCreate(TableBase):
    """创建桌位请求"""
    pass


class TableUpdate(BaseModel):
    """更新桌位请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="桌位名称")
    status: Optional[str] = Field(None, description="状态")


class TableResponse(TableBase):
    """桌位响应"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TableQRCode(BaseModel):
    """桌位二维码响应"""
    table_id: int
    code: str
    name: str
    qrcode_base64: str  # Base64编码的二维码图片
