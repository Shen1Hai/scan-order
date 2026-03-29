from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.dish import router as dish_router
from app.api.table import router as table_router
from app.api.order import router as order_router
from app.api.staff import router as staff_router
from app.api.inventory import router as inventory_router
from app.api.report import router as report_router

__all__ = [
    "auth_router",
    "category_router",
    "dish_router",
    "table_router",
    "order_router",
    "staff_router",
    "inventory_router",
    "report_router"
]
