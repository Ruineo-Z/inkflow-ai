# InkFlow AI - 后端API服务

InkFlow AI 交互式小说平台的后端API服务，基于 FastAPI 构建。

## 项目简介

InkFlow AI 是一个AI驱动的交互式小说平台，用户可以创建和体验由AI生成的交互式故事。本项目为后端API服务，提供用户认证、故事管理、章节生成等核心功能。

## 技术栈

- **框架**: FastAPI
- **数据库**: 外部数据库（通过URL配置）
- **缓存**: 外部Redis（可选，通过URL配置）
- **AI模型**: Google Gemini
- **认证**: JWT
- **容器化**: Docker & Docker Compose

## 项目结构

```
backend/
├── app/
│   ├── api/           # API路由
│   ├── config/        # 配置文件
│   ├── database/      # 数据库配置
│   ├── models/        # 数据模型
│   ├── routes/        # 路由处理
│   ├── services/      # 业务逻辑
│   └── utils/         # 工具函数
├── tests/             # 测试文件
├── requirements.txt   # Python依赖
└── Dockerfile        # Docker配置
```

## 快速开始

### 环境要求

- Python 3.9+
- Docker & Docker Compose
- 外部数据库URL（PostgreSQL/MySQL等）
- 外部Redis URL（可选）

### 使用Docker运行

1. 克隆项目
```bash
git clone <repository-url>
cd inkflow-ai
```

2. 配置环境变量

**Docker部署（推荐）**：
```bash
# 复制Docker环境变量模板
cp .env.example .env
# 编辑 .env 文件，设置数据库URL、API密钥等
```

**本地开发**：
```bash
# 复制本地开发环境变量模板
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，设置本地数据库等配置
```

3. 启动服务
```bash
docker-compose up -d
```

### 本地开发

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. 启动开发服务器
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 20001
```

## API文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: http://localhost:20001/docs
- ReDoc: http://localhost:20001/redoc

## 主要功能

### 用户认证
- 用户注册
- 用户登录
- JWT令牌管理

### 故事管理
- 创建故事
- 获取故事列表
- 获取故事详情
- 获取用户故事

### 章节生成
- AI驱动的章节生成
- 流式内容传输
- 选择分支管理

## 环境变量管理

### 配置文件说明

- **项目根目录 `.env`**: Docker部署专用配置
- **`backend/.env`**: 本地开发专用配置
- **`.env.example`**: Docker部署配置模板
- **`backend/.env.example`**: 本地开发配置模板

### 主要环境变量

| 变量名 | 描述 | Docker部署 | 本地开发 |
|--------|------|------------|----------|
| `DATABASE_URL` | 数据库连接URL | **必需** | **必需** |
| `REDIS_URL` | Redis连接URL | 可选 | 可选 |
| `GEMINI_API_KEY` | Google Gemini API密钥 | **必需** | **必需** |
| `SECRET_KEY` | JWT密钥 | **必需** | **必需** |
| `DEBUG` | 调试模式 | `false` | `true` |
| `CORS_ORIGINS` | 允许的跨域源 | 生产域名 | 本地端口 |

## 部署

### Docker部署

1. 设置环境变量
```bash
# 复制环境变量模板并编辑
cp .env.example .env
# 编辑 .env 文件，填入实际的配置值
```

2. 启动服务
```bash
# 构建并启动后端服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs backend
```

### 生产环境配置

1. 设置强密码和密钥
2. 准备外部数据库服务（PostgreSQL/MySQL等）
3. 准备外部Redis缓存服务（可选）
4. 配置环境变量（DATABASE_URL、REDIS_URL等）
5. 设置反向代理（Nginx）
6. 配置SSL证书

## 开发指南

### 添加新的API端点

1. 在 `app/routes/` 中创建路由文件
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/models/` 中定义数据模型
4. 在 `app/api/` 中注册路由

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

### 运行测试

```bash
cd backend
pytest tests/
```

## 前端项目

前端代码已迁移到独立仓库：[inkflow-ai-frontend](https://github.com/Ruineo-Z/inkflow-ai-frontend)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
