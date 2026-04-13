from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    """
    菜品分类表
    归属商户
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(50), nullable=False, comment="分类名称")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    status = Column(String(20), default="active", comment="状态: active/inactive")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="categories")
    dishes = relationship("Dish", back_populates="category")

    # 同一商户下名称唯一
    __table_args__ = (
        Index('ix_category_merchant_name', 'merchant_id', 'name', unique=True),
    )


from sqlalchemy import Index, Index
