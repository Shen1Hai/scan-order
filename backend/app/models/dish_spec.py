from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class DishSpec(Base):
    """
    菜品规格表
    如: 大份、中份、小份
    """
    __tablename__ = "dish_specs"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False, comment="规格名称，如：大份、中份、小份")
    price = Column(Numeric(10, 2), nullable=False, comment="规格价格")
    is_default = Column(Boolean, default=False, comment="是否默认规格")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    dish = relationship("Dish", back_populates="specs")

    __table_args__ = (
        Index('ix_dish_spec_dish', 'dish_id'),
    )
