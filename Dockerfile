# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "等待数据库服务启动..."\n\
while ! nc -z postgres-server 5432; do\n\
  sleep 1\n\
done\n\
echo "数据库已就绪，开始初始化..."\n\
\n\
# 运行数据库迁移\n\
python -c "from app.database import create_tables; create_tables()" || echo "数据库初始化完成"\n\
\n\
echo "启动应用服务..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 20001\n\
' > /start.sh && chmod +x /start.sh

# 暴露端口
EXPOSE 20001

# 启动命令
CMD ["/start.sh"]
