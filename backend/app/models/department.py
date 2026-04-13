from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Department(Base):
    """部门表（树形结构，支持多级嵌套）"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(50), nullable=False, comment="部门名称")
    code = Column(String(50), nullable=False, comment="部门编码")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="active", comment="状态: active/inactive")
    manager_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True, comment="部门负责人ID")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="departments")
    parent = relationship("Department", remote_side=[id], back_populates="children")
    children = relationship("Department", back_populates="parent", cascade="all, delete-orphan")
    manager = relationship("Staff", foreign_keys="Department.manager_id", back_populates="managed_departments")
    staff = relationship("Staff", back_populates="department", foreign_keys="Staff.department_id")

    # 唯一约束: 同一商户下部门编码唯一
    __table_args__ = (
        Index('ix_department_merchant_code', 'merchant_id', 'code', unique=True),
    )
