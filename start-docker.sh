#!/bin/bash

# InkFlow AI Docker 启动脚本

echo "🚀 启动 InkFlow AI 服务..."

# 检查是否存在 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，正在创建..."
    cp .env.docker .env
    echo "📝 请编辑 .env 文件，填入必要的配置（如 GEMINI_API_KEY）"
    echo "💡 提示：至少需要配置 GEMINI_API_KEY 和 SECRET_KEY"
    read -p "按回车键继续..."
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 服务状态："
docker compose ps

echo ""
echo "✅ 服务启动完成！"
echo "🌐 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:20001"
echo "📚 API文档: http://localhost:20001/docs"
echo ""
echo "📝 查看日志: docker compose logs -f"
echo "🛑 停止服务: docker compose down"
echo "🗑️  清理数据: docker compose down -v"
echo ""
echo "🎉 开始使用 InkFlow AI 吧！"