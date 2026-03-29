from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.dish import router as dish_router
from app.api.dish_ext import router as dish_ext_router
from app.api.table import router as table_router
from app.api.order import router as order_router
from app.api.staff import router as staff_router
from app.api.inventory import router as inventory_router
from app.api.report import router as report_router
from app.api.upload import router as upload_router
from app.api.package import router as package_router
from app.api.coupon import router as coupon_router

__all__ = [
    "auth_router",
    "category_router",
    "dish_router",
    "dish_ext_router",
    "table_router",
    "order_router",
    "staff_router",
    "inventory_router",
    "report_router",
    "upload_router",
    "package_router",
    "coupon_router"
]
