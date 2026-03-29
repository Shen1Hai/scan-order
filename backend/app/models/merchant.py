from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Merchant(Base):
    """
    商户/店铺表
    支持连锁架构：总部创建分店，分店归属总部
    """
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="商户/店铺名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="商户编码")
    contact = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    address = Column(Text, comment="地址")
    status = Column(String(20), default="active", comment="状态: active/inactive")

    # 连锁相关
    parent_id = Column(Integer, ForeignKey("merchants.id"), nullable=True, comment="上级商户ID")
    level = Column(Integer, default=0, comment="层级: 0=总部, 1=分店")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    parent = relationship("Merchant", remote_side=[id], backref="branches")
    roles = relationship("Role", back_populates="merchant", cascade="all, delete-orphan")
    staff = relationship("Staff", back_populates="merchant", cascade="all, delete-orphan")
    tables = relationship("Table", back_populates="merchant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="merchant", cascade="all, delete-orphan")
    dishes = relationship("Dish", back_populates="merchant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="merchant", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="merchant", cascade="all, delete-orphan")
