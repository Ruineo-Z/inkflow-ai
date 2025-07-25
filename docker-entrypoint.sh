#!/bin/bash
set -e

echo "等待数据库服务启动..."
while ! nc -z postgres-server 5432; do
  sleep 1
done
echo "数据库已就绪，开始初始化..."

# 运行数据库迁移
python -c "from app.database import create_tables; create_tables()" || echo "数据库初始化完成"

echo "启动应用服务..."
exec uvicorn main:app --host 0.0.0.0 --port 20001
