"""
系统初始化服务
用于初始化商户、权限、角色等基础数据
"""
from sqlalchemy.orm import Session
from app.models.merchant import Merchant
from app.models.permission import Permission, Role, role_permissions
from app.models.staff import Staff
from app.core.permissions import ALL_PERMISSIONS, SYSTEM_ROLES
from app.core.security import get_password_hash


def init_permissions(db: Session):
    """初始化权限数据"""
    for perm_data in ALL_PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            perm = Permission(
                code=perm_data["code"],
                name=perm_data["name"],
                category=perm_data["category"]
            )
            db.add(perm)

    db.commit()
    print(f"已初始化 {len(ALL_PERMISSIONS)} 个权限")


def init_system_roles(db: Session, merchant_id: int):
    """初始化系统角色"""
    for role_code, role_data in SYSTEM_ROLES.items():
        # 检查角色是否已存在
        existing = db.query(Role).filter(
            Role.merchant_id == merchant_id,
            Role.code == role_code
        ).first()

        if existing:
            continue

        # 创建角色
        role = Role(
            merchant_id=merchant_id,
            code=role_code,
            name=role_data["name"],
            description=role_data["description"],
            is_system=True
        )
        db.add(role)
        db.flush()

        # 绑定权限
        perm_codes = role_data["permissions"]
        if "*" in perm_codes:
            # 拥有所有权限
            all_perms = db.query(Permission).all()
            role.permissions = all_perms
        else:
            # 绑定指定权限
            perms = db.query(Permission).filter(
                Permission.code.in_(perm_codes)
            ).all()
            role.permissions = perms

    db.commit()
    print(f"已为商户 {merchant_id} 初始化 {len(SYSTEM_ROLES)} 个系统角色")


def init_super_admin(db: Session, merchant_id: int):
    """初始化超级管理员"""
    existing = db.query(Staff).filter(
        Staff.merchant_id == merchant_id,
        Staff.username == "admin"
    ).first()

    if existing:
        return existing

    # 获取超级管理员角色
    super_admin_role = db.query(Role).filter(
        Role.merchant_id == merchant_id,
        Role.code == "super_admin"
    ).first()

    admin = Staff(
        merchant_id=merchant_id,
        username="admin",
        password=get_password_hash("admin123"),
        name="超级管理员",
        role_id=super_admin_role.id if super_admin_role else None,
        is_super_admin=True
    )
    db.add(admin)
    db.commit()

    print(f"已为商户 {merchant_id} 创建超级管理员: admin / admin123")
    return admin


def init_merchant(db: Session, name: str, code: str, parent_id: int = None):
    """初始化商户"""
    existing = db.query(Merchant).filter(Merchant.code == code).first()
    if existing:
        print(f"商户 {code} 已存在")
        return existing

    merchant = Merchant(
        name=name,
        code=code,
        parent_id=parent_id,
        level=0 if parent_id is None else 1
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    print(f"已创建商户: {name} ({code})")
    return merchant


def init_sample_data(db: Session):
    """初始化示例数据（单个商户）"""
    # 创建总部商户
    merchant = init_merchant(db, "示例餐厅", "DEMO001")

    # 初始化权限
    init_permissions(db)

    # 初始化系统角色
    init_system_roles(db, merchant.id)

    # 创建超级管理员
    init_super_admin(db, merchant.id)

    return merchant
