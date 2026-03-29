from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ 菜品规格 Schema ============

class DishSpecBase(BaseModel):
    """规格基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="规格名称")
    price: Decimal = Field(..., ge=0, description="规格价格")
    is_default: bool = Field(default=False, description="是否默认")
    sort_order: int = Field(default=0, description="排序")


class DishSpecCreate(DishSpecBase):
    """创建规格请求"""
    pass


class DishSpecUpdate(BaseModel):
    """更新规格请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0)
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None


class DishSpecResponse(DishSpecBase):
    """规格响应"""
    id: int
    dish_id: int

    class Config:
        from_attributes = True


# ============ 菜品做法 Schema ============

class DishCookingBase(BaseModel):
    """做法基础Schema"""
    name: str = Field(..., min_length=1, max_length=50, description="做法名称")
    description: Optional[str] = Field(None, description="描述")
    is_required: bool = Field(default=False, description="是否必选")
    is_default: Optional[str] = Field(None, description="默认选项")
    sort_order: int = Field(default=0, description="排序")
    status: str = Field(default="active", description="状态")


class DishCookingCreate(DishCookingBase):
    """创建做法请求"""
    pass


class DishCookingUpdate(BaseModel):
    """更新做法请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_required: Optional[bool] = None
    is_default: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class DishCookingResponse(DishCookingBase):
    """做法响应"""
    id: int

    class Config:
        from_attributes = True


# ============ 套餐 Schema ============

class PackageItemBase(BaseModel):
    """套餐项基础Schema"""
    dish_id: Optional[int] = Field(None, description="菜品ID")
    dish_name: str = Field(..., description="菜品名称")
    quantity: int = Field(default=1, ge=1, description="数量")
    price: Decimal = Field(default=0, ge=0, description="单价")


class PackageItemCreate(PackageItemBase):
    """创建套餐项请求"""
    pass


class PackageItemResponse(PackageItemBase):
    """套餐项响应"""
    id: int

    class Config:
        from_attributes = True


class DishPackageBase(BaseModel):
    """套餐基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="套餐名称")
    description: Optional[str] = Field(None, description="描述")
    image: Optional[str] = Field(None, description="图片URL")
    price: Decimal = Field(..., ge=0, description="套餐价格")
    original_price: Optional[Decimal] = Field(None, ge=0, description="原价")
    stock: int = Field(default=0, ge=0, description="库存")
    is_recommended: bool = Field(default=False, description="是否推荐")


class DishPackageCreate(DishPackageBase):
    """创建套餐请求"""
    items: List[PackageItemCreate] = Field(default=[], description="套餐包含的菜品")


class DishPackageUpdate(BaseModel):
    """更新套餐请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    image: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    is_recommended: Optional[bool] = None
    status: Optional[str] = None


class DishPackageResponse(DishPackageBase):
    """套餐响应"""
    id: int
    items: List[PackageItemResponse] = []

    class Config:
        from_attributes = True


# ============ 优惠券 Schema ============

class CouponBase(BaseModel):
    """优惠券基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="名称")
    code: str = Field(..., min_length=1, max_length=50, description="优惠码")
    type: str = Field(..., description="类型: cash/discount")
    value: Decimal = Field(..., gt=0, description="优惠值")
    min_amount: Decimal = Field(default=0, description="最低消费")
    max_discount: Optional[Decimal] = Field(None, description="最高优惠")
    total_count: int = Field(default=0, description="发放总量")
    valid_from: datetime = Field(..., description="有效期开始")
    valid_until: datetime = Field(..., description="有效期结束")


class CouponCreate(CouponBase):
    """创建优惠券请求"""
    pass


class CouponUpdate(BaseModel):
    """更新优惠券请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[str] = None
    value: Optional[Decimal] = Field(None, gt=0)
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_discount: Optional[Decimal] = None
    total_count: Optional[int] = Field(None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: Optional[str] = None


class CouponResponse(CouponBase):
    """优惠券响应"""
    id: int
    merchant_id: int
    used_count: int = 0
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponClaimResponse(BaseModel):
    """优惠券领取响应"""
    id: int
    coupon_id: int
    coupon_name: str
    code: str
    type: str
    value: Decimal
    is_used: bool

    class Config:
        from_attributes = True
