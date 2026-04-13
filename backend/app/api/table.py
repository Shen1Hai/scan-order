from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import qrcode

from app.core.database import get_db
from app.core.security import get_current_user, require_permissions
from app.core.config import settings
from app.models.tables import Table
from app.models.staff import Staff
from app.schemas.table import TableCreate, TableUpdate, TableResponse, TableQRCode

router = APIRouter(prefix="/api/tables", tags=["桌位管理"])


def generate_qrcode(data: str) -> str:
    """生成二维码并返回Base64编码"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    import base64
    return base64.b64encode(buffer.getvalue()).decode()


@router.get("", response_model=List[TableResponse])
async def list_tables(
    status: str = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取桌位列表"""
    query = db.query(Table)
    if status:
        query = query.filter(Table.status == status)
    return query.order_by(Table.id).all()


@router.get("/by-code/{code}")
async def get_table_by_code(code: str, db: Session = Depends(get_db)):
    """通过编码获取桌位（扫码入口）"""
    table = db.query(Table).filter(Table.code == code).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌位不存在")
    return {
        "id": table.id,
        "code": table.code,
        "name": table.name,
        "status": table.status
    }


@router.get("/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """获取桌位详情"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌位不存在")
    return table


@router.post("", response_model=TableResponse)
async def create_table(
    table_data: TableCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["table:write"]))
):
    """创建桌位"""
    # 检查编码是否已存在
    existing = db.query(Table).filter(Table.code == table_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="桌位编码已存在")

    table = Table(merchant_id=current_user.merchant_id, **table_data.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.put("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: int,
    table_data: TableUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["table:write"]))
):
    """更新桌位"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌位不存在")

    update_data = table_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)

    db.commit()
    db.refresh(table)
    return table


@router.delete("/{table_id}")
async def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["table:write"]))
):
    """删除桌位"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌位不存在")

    db.delete(table)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{table_id}/qrcode", response_model=TableQRCode)
async def get_table_qrcode(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["table:qrcode"]))
):
    """生成桌位二维码"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌位不存在")

    # 二维码内容：H5点单页面URL + 桌位编码
    qr_content = f"{settings.APP_NAME}://table/{table.code}"
    qrcode_base64 = generate_qrcode(qr_content)

    return {
        "table_id": table.id,
        "code": table.code,
        "name": table.name,
        "qrcode_base64": qrcode_base64
    }


@router.post("/batch-qrcodes")
async def batch_generate_qrcodes(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(require_permissions(["table:qrcode"]))
):
    """批量生成所有桌位二维码"""
    tables = db.query(Table).all()
    result = []
    for table in tables:
        qr_content = f"{settings.APP_NAME}://table/{table.code}"
        qrcode_base64 = generate_qrcode(qr_content)
        result.append({
            "table_id": table.id,
            "code": table.code,
            "name": table.name,
            "qrcode_base64": qrcode_base64
        })
    return result
