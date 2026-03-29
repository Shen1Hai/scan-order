from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
    """
    订单表
    归属商户
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单号")
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    table_name = Column(String(50), comment="桌位名称(冗余)")

    total_amount = Column(Numeric(10, 2), nullable=False, default=0, comment="总金额")
    status = Column(String(20), default="pending", comment="状态: pending/paid/preparing/ready/completed/cancelled")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")

    # 操作员
    operator_id = Column(Integer, ForeignKey("staff.id"), nullable=True, comment="操作员ID")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    operator = relationship("Staff")


class OrderItem(Base):
    """
    订单明细表
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=True)
    dish_name = Column(String(100), nullable=False, comment="菜品名称(冗余)")
    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    quantity = Column(Integer, nullable=False, default=1, comment="数量")

    # 关系
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")
