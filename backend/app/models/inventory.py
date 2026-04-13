from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Inventory(Base):
    """
    库存表
    归属商户
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(100), nullable=False, comment="物品名称")
    quantity = Column(Numeric(10, 2), default=0, comment="数量")
    unit = Column(String(20), default="个", comment="单位")
    low_stock_threshold = Column(Numeric(10, 2), default=10, comment="库存预警阈值")

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="inventory")
    logs = relationship("InventoryLog", back_populates="inventory", cascade="all, delete-orphan")

    # 同一商户下名称唯一
    __table_args__ = (
        Index('ix_inventory_merchant_name', 'merchant_id', 'name', unique=True),
    )


class InventoryLog(Base):
    """
    库存记录表
    """
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)

    type = Column(String(20), nullable=False, comment="类型: in/out")
    quantity = Column(Numeric(10, 2), nullable=False, comment="数量")
    operator_id = Column(Integer, ForeignKey("staff.id"), nullable=True, comment="操作员ID")
    note = Column(Text, comment="备注")

    created_at = Column(DateTime, server_default=func.now())

    # 关系
    inventory = relationship("Inventory", back_populates="logs")
    operator = relationship("Staff")


from sqlalchemy import Index, Index
