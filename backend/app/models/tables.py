from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Table(Base):
    """
    桌位表
    归属商户
    """
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    code = Column(String(20), nullable=False, index=True, comment="桌位编码(二维码)")
    name = Column(String(50), nullable=False, comment="桌位名称")
    status = Column(String(20), default="idle", comment="状态: idle/occupied/reserved")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="tables")
    orders = relationship("Order", back_populates="table")

    # 同一商户下编码唯一
    __table_args__ = (
        Index('ix_table_merchant_code', 'merchant_id', 'code', unique=True),
    )


from sqlalchemy import Index
