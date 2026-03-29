from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from app.core.database import Base


# 菜品-做法关联表
dish_cooking_association = Table(
    "dish_cooking_association",
    Base.metadata,
    Column("dish_id", Integer, ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True),
    Column("cooking_id", Integer, ForeignKey("dish_cookings.id", ondelete="CASCADE"), primary_key=True)
)


class DishCooking(Base):
    """
    菜品做法表
    如: 微辣、中辣、特辣、不要辣
    """
    __tablename__ = "dish_cookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, comment="做法名称")
    description = Column(String(200), nullable=True, comment="描述")
    is_required = Column(Boolean, default=False, comment="是否必选")
    is_default = Column(String(50), nullable=True, comment="默认选项")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="active", comment="状态: active/inactive")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    dishes = relationship("Dish", secondary=dish_cooking_association, back_populates="cooking_methods")


from sqlalchemy import Index
