from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, Boolean, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dish(Base):
    """
    菜品表
    归属商户
    """
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(100), nullable=False, comment="菜品名称")
    price = Column(Numeric(10, 2), nullable=False, comment="价格")
    description = Column(Text, comment="描述")
    image = Column(String(255), comment="图片URL")
    status = Column(String(20), default="active", comment="状态: active/off_sale")
    stock = Column(Integer, default=0, comment="库存")

    # 推荐标记
    is_recommended = Column(Boolean, default=False, comment="是否推荐")
    recommend_type = Column(String(20), nullable=True, comment="推荐类型: hot(热销)/chef(主厨推荐)/new(新品)")

    # 是否为套餐
    is_package = Column(Boolean, default=False, comment="是否套餐")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="dishes")
    category = relationship("Category", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")
    specs = relationship("DishSpec", back_populates="dish", cascade="all, delete-orphan")
    cooking_methods = relationship("DishCooking", secondary="dish_cooking_association", back_populates="dishes")


from sqlalchemy import Index, Index
