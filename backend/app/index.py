"""
扫码点单系统 - FastAPI 后端
支持多商户、RBAC权限管理、连锁架构
"""
import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import app_logger, api_logger
from app.api import (
    auth_router,
    category_router,
    dish_router,
    dish_ext_router,
    table_router,
    order_router,
    staff_router,
    inventory_router,
    report_router,
    upload_router,
    package_router,
    coupon_router,
    role_router,
    department_router
)
from app.api.operation_log import router as operation_log_router
from app.services.websocket import websocket_endpoint
from app.services.init_service import init_sample_data


def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    app_logger.info(f"{'='*50}")
    app_logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    app_logger.info(f"{'='*50}")

    # 创建数据库表
    create_tables()
    app_logger.info("数据库表创建完成")

    # 初始化示例数据
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        init_sample_data(db)
        app_logger.info("示例数据初始化完成")
    except Exception as e:
        app_logger.error(f"初始化数据时出错: {e}")
    finally:
        db.close()

    app_logger.info(f"服务启动完成，访问地址: http://0.0.0.0:{settings.PORT}")
    app_logger.info(f"API 文档: http://0.0.0.0:{settings.PORT}/docs")

    yield

    # 关闭时执行
    app_logger.info("服务关闭中...")
    app_logger.info(f"{settings.APP_NAME} 已关闭")
    app_logger.info(f"{'='*50}")


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
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求日志"""
    start_time = datetime.now()

    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()

        # 记录请求
        api_logger.info(
            f"{request.method} {request.url.path} - "
            f"状态:{response.status_code} - "
            f"耗时:{process_time:.3f}s - "
            f"客户端:{request.client.host if request.client else 'unknown'}"
        )

        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        api_logger.error(
            f"{request.method} {request.url.path} - "
            f"错误:{str(e)} - "
            f"耗时:{process_time:.3f}s"
        )
        raise

# 注册路由
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(dish_router)
app.include_router(dish_ext_router)
app.include_router(table_router)
app.include_router(order_router)
app.include_router(staff_router)
app.include_router(inventory_router)
app.include_router(report_router)
app.include_router(upload_router)
app.include_router(operation_log_router)
app.include_router(package_router)
app.include_router(coupon_router)
app.include_router(role_router)
app.include_router(department_router)

# 静态文件服务 (上传的文件)
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
if UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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
