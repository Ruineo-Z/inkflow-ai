#!/bin/bash

# 等待数据库服务启动
echo "等待数据库服务启动..."
while ! pg_isready -h postgres -p 5432 -U inkflow; do
  echo "数据库未就绪，等待中..."
  sleep 2
done

echo "数据库已就绪，开始初始化..."

# 初始化数据库表
python -c "
from app.database.connection import create_tables
from app.models.user import User
try:
    create_tables()
    print('数据库表初始化完成')
except Exception as e:
    print(f'数据库初始化失败: {e}')
    exit(1)
"

echo "启动应用服务..."

# 启动FastAPI应用
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 20001