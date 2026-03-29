from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Staff(Base):
    """
    员工表
    关联商户和角色
    """
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    username = Column(String(50), nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    name = Column(String(50), nullable=False, comment="姓名")

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, comment="角色ID")

    status = Column(String(20), default="active", comment="状态: active/inactive")
    is_super_admin = Column(Boolean, default=False, comment="是否超级管理员")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="staff")
    role = relationship("Role", back_populates="staff")
    inventory_logs = relationship("InventoryLog", back_populates="operator")

    # 同一商户下用户名唯一
    __table_args__ = (
        Index('ix_staff_merchant_username', 'merchant_id', 'username', unique=True),
    )


# 需要先定义 Role 才能引用，但这里用字符串引用
from sqlalchemy import Index
