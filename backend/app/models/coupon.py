from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Coupon(Base):
    """
    优惠券表
    """
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(100), nullable=False, comment="优惠券名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="优惠码")
    type = Column(String(20), nullable=False, comment="类型: cash(现金券)/discount(折扣)")
    value = Column(Numeric(10, 2), nullable=False, comment="优惠值: 现金券为金额，折扣券为折扣率")
    min_amount = Column(Numeric(10, 2), default=0, comment="最低消费金额")
    max_discount = Column(Numeric(10, 2), nullable=True, comment="最高优惠金额（折扣券用）")

    total_count = Column(Integer, default=0, comment="发放总量")
    used_count = Column(Integer, default=0, comment="已使用数量")

    valid_from = Column(DateTime, nullable=False, comment="有效期开始")
    valid_until = Column(DateTime, nullable=False, comment="有效期结束")

    status = Column(String(20), default="active", comment="状态: active/inactive/published")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant")
    claims = relationship("CouponClaim", back_populates="coupon", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_coupon_merchant', 'merchant_id'),
        Index('ix_coupon_code', 'code'),
    )


class CouponClaim(Base):
    """
    优惠券领取记录
    """
    __tablename__ = "coupon_claims"

    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    user_identifier = Column(String(100), nullable=True, comment="领取人标识（手机号或桌位）")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="关联订单")
    is_used = Column(Boolean, default=False, comment="是否已使用")
    used_at = Column(DateTime, nullable=True, comment="使用时间")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    coupon = relationship("Coupon", back_populates="claims")
    order = relationship("Order")


from sqlalchemy import Index, Index
