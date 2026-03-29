"""
操作日志服务
记录用户在后台的增删改操作
"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.operation_log import OperationLog


class OperationLogService:
    """操作日志服务"""

    def __init__(self, db: Session, operator_id: int = None, operator_name: str = None):
        self.db = db
        self.operator_id = operator_id
        self.operator_name = operator_name

    def log(
        self,
        action: str,
        module: str,
        target_type: str = None,
        target_id: int = None,
        target_name: str = None,
        detail: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        merchant_id: int = None
    ):
        """
        记录操作日志

        Args:
            action: 操作类型 (create/update/delete)
            module: 模块名称 (menu/order/table/staff/inventory)
            target_type: 对象类型
            target_id: 对象ID
            target_name: 对象名称
            detail: 详细信息 (dict，会转为JSON字符串)
            ip_address: IP地址
            user_agent: User Agent
            merchant_id: 商户ID
        """
        log_entry = OperationLog(
            merchant_id=merchant_id or (self.db.query(OperationLog).filter_by(merchant_id=self.operator_id).first() and getattr(self, 'merchant_id', None)),
            operator_id=self.operator_id,
            operator_name=self.operator_name,
            action=action,
            module=module,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            detail=str(detail) if detail else None,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.db.add(log_entry)
        self.db.commit()

        return log_entry

    def log_create(self, module: str, target_type: str, target_id: int, target_name: str = None, detail: dict = None, merchant_id: int = None):
        """记录创建操作"""
        return self.log(
            action="create",
            module=module,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            detail=detail,
            merchant_id=merchant_id
        )

    def log_update(self, module: str, target_type: str, target_id: int, target_name: str = None, detail: dict = None, merchant_id: int = None):
        """记录更新操作"""
        return self.log(
            action="update",
            module=module,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            detail=detail,
            merchant_id=merchant_id
        )

    def log_delete(self, module: str, target_type: str, target_id: int, target_name: str = None, merchant_id: int = None):
        """记录删除操作"""
        return self.log(
            action="delete",
            module=module,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            merchant_id=merchant_id
        )

    def log_login(self, detail: dict = None, merchant_id: int = None):
        """记录登录操作"""
        return self.log(
            action="login",
            module="auth",
            target_type="staff",
            target_id=self.operator_id,
            target_name=self.operator_name,
            detail=detail,
            merchant_id=merchant_id
        )


def get_operation_logs(
    db: Session,
    merchant_id: int = None,
    operator_id: int = None,
    module: str = None,
    action: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    page_size: int = 50
):
    """
    获取操作日志列表

    Args:
        merchant_id: 商户ID
        operator_id: 操作人ID
        module: 模块名称
        action: 操作类型
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        page_size: 每页数量

    Returns:
        日志列表和总数
    """
    query = db.query(OperationLog)

    if merchant_id:
        query = query.filter(OperationLog.merchant_id == merchant_id)
    if operator_id:
        query = query.filter(OperationLog.operator_id == operator_id)
    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date + " 23:59:59")

    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return logs, total
