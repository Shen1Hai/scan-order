from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class OperationLog(Base):
    """
    操作日志表
    记录用户在后台的操作行为
    """
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    # 操作人
    operator_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    operator_name = Column(String(50), nullable=True)

    # 操作类型
    action = Column(String(50), nullable=False, comment="操作类型: create/update/delete/login")
    module = Column(String(50), nullable=False, comment="模块: menu/order/table/staff/inventory")

    # 操作对象
    target_type = Column(String(50), nullable=True, comment="对象类型")
    target_id = Column(Integer, nullable=True, comment="对象ID")
    target_name = Column(String(200), nullable=True, comment="对象名称")

    # 操作详情
    detail = Column(Text, nullable=True, comment="操作详情(JSON)")

    # 客户端信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="User Agent")

    created_at = Column(DateTime, server_default=func.now())

    # 关系
    operator = relationship("Staff")
    merchant = relationship("Merchant")

    # 索引
    __table_args__ = (
        Index('ix_log_merchant_created', 'merchant_id', 'created_at'),
        Index('ix_log_operator_created', 'operator_id', 'created_at'),
        Index('ix_log_action_module', 'action', 'module'),
    )


from sqlalchemy import Index, Index
