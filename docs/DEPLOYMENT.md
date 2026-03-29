# 扫码点单系统 - 部署与操作手册

## 版本信息

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2026-03-29 | 初始版本：FastAPI后端 + 多商户架构 + RBAC权限 |
| v1.1.0 | (待完成) | H5顾客端 + Vue后台管理 |
| v1.2.0 | (待完成) | 微信小程序 |

---

## 仓库信息

- **GitHub**: https://github.com/Shen1Hai/scan-order
- **分支**: main

---

## 一、环境准备

### 1.1 安装 Python

要求：Python 3.9+

```bash
# 检查 Python 版本
python --version

# 如果没有，安装 Python 3.9+
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.9
```

### 1.2 安装 PostgreSQL

要求：PostgreSQL 13+

```bash
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql@13
# Ubuntu: sudo apt install postgresql-13
```

### 1.3 安装 Git

```bash
# 检查
git --version

# Windows: https://git-scm.com/download/win
# macOS: brew install git
```

---

## 二、克隆项目

```bash
# 克隆代码
git clone https://github.com/Shen1Hai/scan-order.git

# 进入项目目录
cd scan-order
```

---

## 三、后端部署

### 3.1 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3.2 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

**依赖列表** (`backend/requirements.txt`)：
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
python-qrcode==7.4.2
Pillow==10.2.0
websockets==12.0
alembic==1.13.1
```

### 3.3 配置数据库

#### 3.3.1 创建数据库

```bash
# 登录 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE scanorder;
CREATE USER scanorder_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE scanorder TO scanorder_user;

# 退出
\q
```

#### 3.3.2 修改配置

编辑 `backend/app/core/config.py`：

```python
# 数据库配置
DB_HOST: str = "localhost"
DB_PORT: int = 5432
DB_USER: str = "scanorder_user"
DB_PASSWORD: str = "your_password"  # 修改为你的密码
DB_NAME: str = "scanorder"

# JWT 密钥（生产环境请修改）
SECRET_KEY: str = "your-secret-key-change-in-production"
```

### 3.4 启动服务

```bash
# 开发模式启动
python main.py

# 或使用 uvicorn
uvicorn app.index:app --reload --port 8000

# 生产模式启动
uvicorn app.index:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3.5 验证后端

```bash
# 检查健康状态
curl http://localhost:8000/health

# 访问 API 文档
# 浏览器打开: http://localhost:8000/docs
```

**预期输出**：
```json
{"status": "ok"}
```

### 3.6 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |

---

## 四、Git 推送流程

### 4.1 首次推送（如已克隆则跳过）

```bash
git remote add origin https://github.com/Shen1Hai/scan-order.git
git branch -M main
git push -u origin main
```

### 4.2 日常开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature-name

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到远程
git push -u origin feature/your-feature-name

# 4. 在 GitHub 创建 Pull Request
# 访问: https://github.com/Shen1Hai/scan-order
```

### 4.3 拉取最新代码

```bash
# 切换到 main 分支
git checkout main

# 拉取最新代码
git pull origin main

# 重新安装依赖（如有变更）
pip install -r requirements.txt
```

---

## 五、版本发布流程

### 5.1 创建版本标签

```bash
# 切换到 main 分支并拉取最新
git checkout main
git pull origin main

# 创建版本标签
git tag -a v1.0.0 -m "版本 v1.0.0: 初始版本"

# 推送标签
git push origin v1.0.0
```

### 5.2 发布检查清单

- [ ] 所有功能测试通过
- [ ] API 文档完整
- [ ] README.md 已更新
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已记录

---

## 六、项目结构

```
scan-order/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证
│   │   │   ├── category.py    # 分类管理
│   │   │   ├── dish.py        # 菜品管理
│   │   │   ├── table.py       # 桌位管理
│   │   │   ├── order.py       # 订单管理
│   │   │   ├── staff.py       # 员工管理
│   │   │   ├── inventory.py   # 库存管理
│   │   │   └── report.py      # 报表统计
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py   # 数据库连接
│   │   │   ├── security.py    # 安全/权限
│   │   │   └── permissions.py # 权限定义
│   │   ├── models/            # 数据模型
│   │   │   ├── merchant.py    # 商户模型
│   │   │   ├── permission.py  # 权限/角色模型
│   │   │   ├── staff.py       # 员工模型
│   │   │   ├── tables.py      # 桌位模型
│   │   │   ├── category.py    # 分类模型
│   │   │   ├── dish.py        # 菜品模型
│   │   │   ├── order.py        # 订单模型
│   │   │   └── inventory.py   # 库存模型
│   │   ├── schemas/           # Pydantic 模型
│   │   └── services/          # 业务服务
│   │       ├── websocket.py   # WebSocket 服务
│   │       └── init_service.py # 初始化服务
│   ├── main.py
│   └── requirements.txt
├── h5/                         # H5 顾客端 (待完成)
├── admin/                      # 后台管理前端 (待完成)
├── mini-program/               # 微信小程序 (待完成)
├── docs/                       # 文档
│   └── DEPLOYMENT.md          # 本文档
├── README.md                   # 项目说明
└── .gitignore
```

---

## 七、常见问题

### Q1: 启动报错 `ModuleNotFoundError`

```bash
# 重新安装依赖
pip install -r requirements.txt
```

### Q2: 数据库连接失败

```bash
# 检查 PostgreSQL 是否启动
# Windows:
net start postgresql

# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql
```

### Q3: 端口被占用

```bash
# 修改端口 (backend/app/core/config.py)
# 添加: PORT: int = 8001

# 或启动时指定
uvicorn app.index:app --port 8001
```

### Q4: Git 推送需要认证

```bash
# 使用 Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/Shen1Hai/scan-order.git
```

---

## 八、后续开发

### v1.1.0 待完成功能

- [ ] H5 顾客端开发
- [ ] Vue 后台管理前端
- [ ] 实时订单推送完善

### v1.2.0 待完成功能

- [ ] 微信小程序开发
- [ ] 真实微信支付对接
