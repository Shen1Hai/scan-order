from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DishPackage(Base):
    """
    套餐表
    套餐是一组菜品的组合
    """
    __tablename__ = "dish_packages"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(100), nullable=False, comment="套餐名称")
    description = Column(String(500), nullable=True, comment="套餐描述")
    image = Column(String(255), nullable=True, comment="套餐图片")
    price = Column(Numeric(10, 2), nullable=False, comment="套餐价格")
    original_price = Column(Numeric(10, 2), nullable=True, comment="原价（划线价格）")

    status = Column(String(20), default="active", comment="状态: active/off_sale")
    stock = Column(Integer, default=0, comment="库存")

    # 推荐标记
    is_recommended = Column(Boolean, default=False, comment="是否推荐")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant")
    items = relationship("PackageItem", back_populates="package", cascade="all, delete-orphan")


class PackageItem(Base):
    """
    套餐明细表
    记录套餐包含的菜品
    """
    __tablename__ = "package_items"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("dish_packages.id", ondelete="CASCADE"), nullable=False)

    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=True, comment="关联菜品，可为空表示已删除的菜品")
    dish_name = Column(String(100), nullable=False, comment="菜品名称（冗余）")
    quantity = Column(Integer, default=1, comment="数量")
    price = Column(Numeric(10, 2), default=0, comment="菜品单价（快照）")

    created_at = Column(DateTime, server_default=func.now())

    # 关系
    package = relationship("DishPackage", back_populates="items")
    dish = relationship("Dish")


from sqlalchemy import Index
