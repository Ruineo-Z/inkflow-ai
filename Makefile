.PHONY: help install dev test clean run docker-build docker-run

# 默认目标
help:
	@echo "InkFlow AI - 可用命令:"
	@echo "  install     - 安装依赖"
	@echo "  dev         - 开发模式启动服务器"
	@echo "  test        - 运行测试"
	@echo "  clean       - 清理缓存文件"
	@echo "  run         - 生产模式启动服务器"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run  - 运行Docker容器"

# 安装依赖
install:
	uv sync

# 开发模式启动
dev:
	uv run uvicorn main:app --host 0.0.0.0 --port 20001 --reload

# 运行测试
test:
	uv run pytest tests/ -v

# 清理缓存
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# 生产模式启动
run:
	uv run uvicorn main:app --host 0.0.0.0 --port 20001

# Docker构建
docker-build:
	docker build -t inkflow-ai .

# Docker运行
docker-run:
	docker compose up -d
