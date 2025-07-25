#!/usr/bin/env python3
"""
InkFlow AI - AI交互式小说平台
主应用入口文件
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import stories_router, chapters_router, auth_router
from app.database import engine, Base, is_redis_connected, create_tables
from app.utils.exceptions import register_exception_handlers
from app.models.responses import HealthCheckResponse, RootResponse
from app.utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

# 创建数据库表
logger.info("正在初始化数据库表...")
create_tables()
logger.info("数据库表初始化完成")

# 创建FastAPI应用
logger.info("正在创建FastAPI应用...")
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)
logger.info(f"FastAPI应用创建完成: {settings.app_name} v{settings.app_version}")

# 注册异常处理器
logger.info("正在注册异常处理器...")
register_exception_handlers(app)

# 配置CORS
logger.info("正在配置CORS中间件...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 添加版本控制
logger.info("正在注册API路由...")
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(stories_router, prefix=settings.api_prefix)
app.include_router(chapters_router, prefix=settings.api_prefix)
logger.info(f"API路由注册完成，前缀: {settings.api_prefix}")

@app.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    """根路径"""
    return RootResponse(
        message="AI Interactive Novel API",
        version=settings.app_version,
        status="running"
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """健康检查"""
    logger.debug("执行健康检查...")
    redis_status = is_redis_connected()

    status = "healthy" if redis_status else "degraded"
    logger.info(f"健康检查完成 - 状态: {status}, Redis: {'连接' if redis_status else '断开'}")

    return HealthCheckResponse(
        status=status,
        version=settings.app_version,
        services={
            "database": "connected",
            "redis": "connected" if redis_status else "disconnected"
        }
    )

if __name__ == "__main__":
    logger.info("启动InkFlow AI服务器...")
    logger.info(f"服务器配置 - Host: 0.0.0.0, Port: 20001, Debug: {settings.debug}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=20001,
        reload=settings.debug
    )
