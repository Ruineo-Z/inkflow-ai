# Docker Compose 部署指南

本项目提供了完整的 Docker Compose 配置，可以一键启动所有服务。

## 服务架构

- **Frontend (前端)**: React + Vite 应用，运行在端口 3000
- **Backend (后端)**: FastAPI 应用，运行在端口 20001
- **PostgreSQL**: 数据库服务，运行在端口 5432
- **Redis**: 缓存服务，运行在端口 6379

## 快速开始

### 1. 环境配置

复制环境变量模板文件：
```bash
cp .env.docker .env
```

编辑 `.env` 文件，填入必要的配置：
```bash
# 必须配置的项目
GEMINI_API_KEY=your-actual-gemini-api-key
SECRET_KEY=your-super-secret-key-change-this
```

### 2. 启动服务

启动所有服务：
```bash
docker-compose up -d
```

查看服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:20001
- **API文档**: http://localhost:20001/docs

### 4. 停止服务

```bash
# 停止服务
docker-compose down

# 停止服务并删除数据卷（谨慎使用）
docker-compose down -v
```

## 开发模式

如果需要在开发模式下运行（支持热重载）：

```bash
# 仅启动数据库和Redis
docker-compose up -d postgres redis

# 本地运行后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 20001 --reload

# 本地运行前端
npm run dev
```

## 数据持久化

- PostgreSQL 数据存储在 `postgres_data` 数据卷中
- Redis 数据存储在 `redis_data` 数据卷中
- 数据在容器重启后会保持

## 故障排除

### 常见问题

1. **端口冲突**
   - 确保端口 3000、20001、5432、6379 未被占用
   - 可以在 `docker-compose.yml` 中修改端口映射

2. **数据库连接失败**
   - 检查 PostgreSQL 容器是否正常启动
   - 查看后端日志确认数据库连接配置

3. **API 请求失败**
   - 确认 GEMINI_API_KEY 配置正确
   - 检查后端服务是否正常运行

### 重置数据库

如果需要重置数据库：
```bash
docker-compose down -v
docker-compose up -d
```

## 生产部署注意事项

1. **安全配置**
   - 修改默认的数据库密码
   - 使用强密码作为 SECRET_KEY
   - 配置适当的 CORS_ORIGINS

2. **性能优化**
   - 考虑使用外部数据库服务
   - 配置适当的资源限制
   - 启用日志轮转

3. **监控**
   - 添加健康检查
   - 配置日志收集
   - 设置告警机制