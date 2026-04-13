"""
数据库迁移脚本
创建 departments 表并添加 department_id 到 staff 表
"""
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine

def migrate():
    """执行数据库迁移"""
    print("开始数据库迁移...")

    with engine.connect() as conn:
        # 1. 创建 departments 表
        print("创建 departments 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                merchant_id INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
                parent_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                name VARCHAR(50) NOT NULL,
                code VARCHAR(50) NOT NULL,
                sort_order INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active',
                manager_id INTEGER REFERENCES staff(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        print("departments 表创建完成")

        # 2. 创建 unique constraint for department code per merchant
        print("创建部门编码唯一约束...")
        try:
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_department_merchant_code
                ON departments(merchant_id, code)
            """))
            conn.commit()
        except Exception as e:
            print(f"约束已存在或创建失败: {e}")

        # 3. 添加 department_id 列到 staff 表
        print("添加 department_id 列到 staff 表...")
        try:
            conn.execute(text("""
                ALTER TABLE staff
                ADD COLUMN IF NOT EXISTS department_id INTEGER
                REFERENCES departments(id) ON DELETE SET NULL
            """))
            conn.commit()
            print("department_id 列添加完成")
        except Exception as e:
            print(f"列已存在或添加失败: {e}")

        # 4. 添加 index on department_id
        print("创建 department_id 索引...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_staff_department_id
                ON staff(department_id)
            """))
            conn.commit()
        except Exception as e:
            print(f"索引已存在或创建失败: {e}")

        # 5. 添加 parent_id 索引到 departments
        print("创建 parent_id 索引...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_departments_parent_id
                ON departments(parent_id)
            """))
            conn.commit()
        except Exception as e:
            print(f"索引已存在或创建失败: {e}")

    print("数据库迁移完成!")
    print("\n迁移摘要:")
    print("  - 创建 departments 表")
    print("  - 添加 department_id 列到 staff 表")
    print("  - 创建必要的索引")

if __name__ == "__main__":
    migrate()