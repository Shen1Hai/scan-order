# 扫码点单系统

支持多商户、连锁架构的扫码点单系统。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + PostgreSQL
- **前端**: Vue 3 + Element Plus
- **H5**: 原生 HTML/CSS/JS
- **小程序**: 微信小程序
- **实时通信**: WebSocket

## 功能特性

### 多商户支持
- 总部-分店连锁架构
- 独立数据隔离
- 统一管理

### 权限管理 (RBAC)
- 超级管理员、店长、收银员、后厨、服务员
- 细粒度权限控制
- 自定义角色权限

### 顾客端 (H5/小程序)
- 扫码点单
- 购物车
- 模拟支付
- 订单历史

### 后台管理
- 仪表盘统计
- 菜单/分类管理
- 桌位管理 + 二维码生成
- 订单实时推送
- 员工管理
- 库存管理
- 报表统计

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt

# 配置数据库连接 (.env 或直接修改 config.py)
# 默认连接本地 PostgreSQL

# 启动服务
python main.py
# 或
uvicorn app.index:app --reload --port 8000
```

### 前置条件
- Python 3.9+
- PostgreSQL 13+
- Node.js 16+ (for admin frontend)

## 默认账号

- 超级管理员: `admin` / `admin123`

## API 文档

启动后访问: http://localhost:8000/docs

## 项目结构

```
scan-order/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 模型
│   │   └── services/    # 业务服务
│   └── main.py
├── h5/                  # H5 顾客端
├── admin/               # 后台管理前端
└── mini-program/        # 微信小程序
```
