from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.models.staff import Staff
from app.services.operation_log import get_operation_logs
from pydantic import BaseModel

router = APIRouter(prefix="/api/operation-logs", tags=["操作日志"])


class OperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    action: str
    module: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    target_name: Optional[str] = None
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[OperationLogResponse])
async def list_operation_logs(
    operator_id: int = Query(None, description="操作人ID"),
    module: str = Query(None, description="模块"),
    action: str = Query(None, description="操作类型"),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["report:logs"]))
):
    """
    获取操作日志列表
    需要 report:logs 权限
    """
    logs, total = get_operation_logs(
        db=db,
        merchant_id=current_user.merchant_id if not current_user.is_super_admin else None,
        operator_id=operator_id,
        module=module,
        action=action,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )

    return [
        {
            "id": log.id,
            "operator_id": log.operator_id,
            "operator_name": log.operator_name,
            "action": log.action,
            "module": log.module,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "target_name": log.target_name,
            "detail": log.detail,
            "ip_address": log.ip_address,
            "created_at": str(log.created_at)
        }
        for log in logs
    ]
