"""
扫码点单系统 - FastAPI 后端
支持多商户、RBAC权限管理、连锁架构
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import (
    auth_router,
    category_router,
    dish_router,
    table_router,
    order_router,
    staff_router,
    inventory_router,
    report_router
)
from app.services.websocket import websocket_endpoint
from app.services.init_service import init_sample_data


def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    create_tables()

    # 初始化示例数据
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        init_sample_data(db)
    except Exception as e:
        print(f"初始化数据时出错: {e}")
    finally:
        db.close()

    yield
    # 关闭时执行


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="扫码点单系统 - 支持多商户、连锁、RBAC权限",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(dish_router)
app.include_router(table_router)
app.include_router(order_router)
app.include_router(staff_router)
app.include_router(inventory_router)
app.include_router(report_router)

# WebSocket 端点
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    return {
        "message": "扫码点单系统 API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.index:app", host="0.0.0.0", port=8000, reload=True)
