from fastapi import WebSocket
from typing import Set
import json

# 存储所有连接的客户端
active_connections: Set[WebSocket] = set()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接处理"""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")
    except Exception:
        pass
    finally:
        active_connections.discard(websocket)


async def broadcast(message: dict):
    """广播消息给所有客户端"""
    message_json = json.dumps(message, default=str)
    for connection in active_connections.copy():
        try:
            await connection.send_text(message_json)
        except Exception:
            active_connections.discard(connection)


async def notify_new_order(order):
    """通知新订单（后台管理页面实时刷新）"""
    await broadcast({
        "type": "new_order",
        "data": {
            "id": order.id,
            "order_no": order.order_no,
            "table_name": order.table_name,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": str(order.created_at)
        }
    })


async def notify_order_status_change(order_no: str, status: str):
    """通知订单状态变更（顾客端）"""
    await broadcast({
        "type": "order_status",
        "data": {"order_no": order_no, "status": status}
    })


async def notify_low_stock(item: dict):
    """通知库存不足"""
    await broadcast({
        "type": "low_stock",
        "data": item
    })
