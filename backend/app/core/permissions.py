"""
系统权限定义
"""

# 权限分类
PERMISSION_CATEGORIES = {
    "menu": "菜单管理",
    "order": "订单管理",
    "table": "桌位管理",
    "category": "分类管理",
    "dish": "菜品管理",
    "staff": "员工管理",
    "role": "角色管理",
    "inventory": "库存管理",
    "report": "报表统计",
    "merchant": "商户管理",
    "coupon": "优惠券管理",
    "system": "系统设置"
}

# 所有权限定义
ALL_PERMISSIONS = [
    # 商户权限
    {"code": "merchant:read", "name": "查看商户", "category": "merchant"},
    {"code": "merchant:write", "name": "管理商户", "category": "merchant"},
    {"code": "merchant:branch", "name": "管理分店", "category": "merchant"},

    # 菜单/分类权限
    {"code": "category:read", "name": "查看分类", "category": "category"},
    {"code": "category:write", "name": "管理分类", "category": "category"},

    # 菜品权限
    {"code": "dish:read", "name": "查看菜品", "category": "dish"},
    {"code": "dish:write", "name": "管理菜品", "category": "dish"},

    # 桌位权限
    {"code": "table:read", "name": "查看桌位", "category": "table"},
    {"code": "table:write", "name": "管理桌位", "category": "table"},
    {"code": "table:qrcode", "name": "生成二维码", "category": "table"},

    # 订单权限
    {"code": "order:read", "name": "查看订单", "category": "order"},
    {"code": "order:create", "name": "创建订单", "category": "order"},
    {"code": "order:update", "name": "更新订单", "category": "order"},
    {"code": "order:cancel", "name": "取消订单", "category": "order"},
    {"code": "order:pay", "name": "订单支付", "category": "order"},

    # 员工权限
    {"code": "staff:read", "name": "查看员工", "category": "staff"},
    {"code": "staff:write", "name": "管理员工", "category": "staff"},

    # 角色权限
    {"code": "role:read", "name": "查看角色", "category": "role"},
    {"code": "role:write", "name": "管理角色", "category": "role"},

    # 库存权限
    {"code": "inventory:read", "name": "查看库存", "category": "inventory"},
    {"code": "inventory:write", "name": "管理库存", "category": "inventory"},
    {"code": "inventory:log", "name": "库存记录", "category": "inventory"},

    # 报表权限
    {"code": "report:sales", "name": "销售报表", "category": "report"},
    {"code": "report:dishes", "name": "菜品报表", "category": "report"},
    {"code": "report:staff", "name": "员工业绩", "category": "report"},
    {"code": "report:dashboard", "name": "仪表盘", "category": "report"},

    # 优惠券权限
    {"code": "coupon:read", "name": "查看优惠券", "category": "coupon"},
    {"code": "coupon:write", "name": "管理优惠券", "category": "coupon"},

    # 系统权限
    {"code": "system:config", "name": "系统配置", "category": "system"},
]

# 系统内置角色
SYSTEM_ROLES = {
    "super_admin": {
        "name": "超级管理员",
        "description": "拥有系统所有权限",
        "permissions": ["*"]  # * 表示所有权限
    },
    "manager": {
        "name": "店长",
        "description": "拥有门店管理权限",
        "permissions": [
            "merchant:read",
            "category:read", "category:write",
            "dish:read", "dish:write",
            "table:read", "table:write", "table:qrcode",
            "order:read", "order:create", "order:update", "order:cancel", "order:pay",
            "staff:read", "staff:write",
            "role:read",
            "inventory:read", "inventory:write", "inventory:log",
            "report:sales", "report:dishes", "report:staff", "report:dashboard",
            "coupon:read", "coupon:write",
        ]
    },
    "cashier": {
        "name": "收银员",
        "description": "负责收银和订单处理",
        "permissions": [
            "dish:read",
            "table:read",
            "order:read", "order:create", "order:update", "order:pay",
            "inventory:read",
            "report:dashboard",
        ]
    },
    "cook": {
        "name": "后厨",
        "description": "负责订单制作",
        "permissions": [
            "dish:read",
            "order:read", "order:update",
        ]
    },
    "waiter": {
        "name": "服务员",
        "description": "负责点单和服务",
        "permissions": [
            "dish:read",
            "table:read",
            "order:read", "order:create",
        ]
    }
}
