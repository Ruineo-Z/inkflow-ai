from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "AI Interactive Novel API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 数据库配置
    database_url: str = "postgresql://admin:admin@localhost:5432/ai_novel"

    # AI配置
    gemini_api_key: str = ""
    gemini_model: str = "gemini-pro"

    # API配置
    api_prefix: str = "/api"
    cors_origins: List[str] = ["*"]

    # 安全配置
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 内容生成配置
    max_chapter_length: int = 3000
    min_chapter_length: int = 2000
    choices_count: int = 3

    # Redis配置
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 实例化配置
settings = Settings()