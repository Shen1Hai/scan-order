from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from app.core.database import Base

# 角色-权限关联表
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)


class Permission(Base):
    """
    权限表
    定义系统中所有的权限点
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="权限编码")
    name = Column(String(50), nullable=False, comment="权限名称")
    category = Column(String(50), nullable=False, comment="权限分类: menu/order/staff/report/inventory/system")
    description = Column(String(200), comment="权限描述")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class Role(Base):
    """
    角色表
    每个商户可以有多个角色，角色绑定权限
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False, comment="角色编码")
    name = Column(String(50), nullable=False, comment="角色名称")
    description = Column(String(200), comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否系统内置角色")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    staff = relationship("Staff", back_populates="role")

    # 唯一约束: 同一商户下角色编码唯一
    __table_args__ = (
        Index('ix_role_merchant_code', 'merchant_id', 'code', unique=True),
    )


# 需要先定义 Role 才能引用 Index
from sqlalchemy import Index
