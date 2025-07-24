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

# 创建数据库表
create_tables()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(stories_router, prefix=settings.api_prefix)
app.include_router(chapters_router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Interactive Novel API",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    redis_status = is_redis_connected()

    return {
        "status": "healthy" if redis_status else "degraded",
        "version": settings.app_version,
        "services": {
            "database": "connected",
            "redis": "connected" if redis_status else "disconnected"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=20001,
        reload=settings.debug
    )
