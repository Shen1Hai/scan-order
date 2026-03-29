from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.staff import Staff
from app.models.coupon import Coupon, CouponClaim
from app.schemas.dish_ext import CouponCreate, CouponUpdate, CouponResponse

router = APIRouter(prefix="/api/coupons", tags=["优惠券管理"])


@router.get("", response_model=List[CouponResponse])
async def list_coupons(
    status: str = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取优惠券列表"""
    merchant_id = current_user.merchant_id if not current_user.is_super_admin else None

    query = db.query(Coupon)
    if merchant_id:
        query = query.filter(Coupon.merchant_id == merchant_id)
    if status:
        query = query.filter(Coupon.status == status)

    coupons = query.order_by(Coupon.created_at.desc()).all()
    return coupons


@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(coupon_id: int, db: Session = Depends(get_db)):
    """获取优惠券详情"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return coupon


@router.get("/code/{code}", response_model=CouponResponse)
async def get_coupon_by_code(code: str, db: Session = Depends(get_db)):
    """通过优惠码获取优惠券"""
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    return coupon


@router.post("", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["coupon:write"]))
):
    """创建优惠券"""
    merchant_id = current_user.merchant_id if not current_user.is_super_admin else 1

    # 检查优惠码是否已存在
    existing = db.query(Coupon).filter(Coupon.code == coupon_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="优惠码已存在")

    coupon = Coupon(
        merchant_id=merchant_id,
        **coupon_data.model_dump()
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["coupon:write"]))
):
    """更新优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    update_data = coupon_data.model_dump(exclude_unset=True)

    # 检查优惠码冲突
    if update_data.get("code"):
        existing = db.query(Coupon).filter(
            Coupon.code == update_data["code"],
            Coupon.id != coupon_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="优惠码已存在")

    for key, value in update_data.items():
        setattr(coupon, key, value)

    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["coupon:write"]))
):
    """删除优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    db.delete(coupon)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{coupon_id}/publish")
async def publish_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["coupon:write"]))
):
    """发布优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    if coupon.status != "active":
        raise HTTPException(status_code=400, detail="只有激活状态的优惠券才能发布")

    coupon.status = "published"
    db.commit()
    return {"message": "发布成功"}


@router.post("/claim")
async def claim_coupon(
    code: str = Query(..., description="优惠码"),
    user_identifier: str = Query(None, description="领取人标识"),
    db: Session = Depends(get_db)
):
    """领取优惠券"""
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    if coupon.status != "published":
        raise HTTPException(status_code=400, detail="优惠券未发布或已下架")

    now = datetime.now()
    if coupon.valid_from > now or coupon.valid_until < now:
        raise HTTPException(status_code=400, detail="优惠券不在有效期内")

    if coupon.total_count > 0 and coupon.used_count >= coupon.total_count:
        raise HTTPException(status_code=400, detail="优惠券已领完")

    # 检查是否已领取
    if user_identifier:
        existing = db.query(CouponClaim).filter(
            CouponClaim.coupon_id == coupon.id,
            CouponClaim.user_identifier == user_identifier
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="您已领取过该优惠券")

    # 领取
    claim = CouponClaim(
        coupon_id=coupon.id,
        user_identifier=user_identifier
    )
    db.add(claim)

    # 更新已使用数量
    coupon.used_count += 1

    db.commit()
    db.refresh(claim)

    return {
        "message": "领取成功",
        "claim_id": claim.id,
        "coupon": coupon
    }


@router.get("/{coupon_id}/calculate")
async def calculate_discount(
    coupon_id: int,
    order_amount: float = Query(..., description="订单金额"),
    db: Session = Depends(get_db)
):
    """计算优惠券折扣"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    if order_amount < float(coupon.min_amount):
        return {
            "discount": 0,
            "message": f"订单金额需达到 {coupon.min_amount} 元"
        }

    if coupon.type == "cash":
        # 现金券
        discount = float(coupon.value)
    else:
        # 折扣券
        discount = order_amount * (1 - float(coupon.value) / 100)
        if coupon.max_discount and discount > float(coupon.max_discount):
            discount = float(coupon.max_discount)

    final_amount = max(0, order_amount - discount)

    return {
        "original_amount": order_amount,
        "discount": round(discount, 2),
        "final_amount": round(final_amount, 2)
    }
