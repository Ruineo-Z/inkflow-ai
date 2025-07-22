from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseModel):
    # 应用配置
    app_name: str = "AI Interactive Novel API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "postgresql://user:password@localhost:5432/ai_novel_db"
    
    # AI配置
    gemini_api_key: str = ""
    gemini_model: str = "gemini-pro"
    
    # API配置
    api_prefix: str = "/api"
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 内容生成配置
    max_chapter_length: int = 3000
    min_chapter_length: int = 2000
    choices_count: int = 3
    
    def __init__(self, **kwargs):
        # 从环境变量加载配置
        env_values = {
            'app_name': os.getenv('APP_NAME', 'AI Interactive Novel API'),
            'app_version': os.getenv('APP_VERSION', '1.0.0'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///./ai_novel.db'),
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'gemini_model': os.getenv('GEMINI_MODEL', 'gemini-pro'),
            'api_prefix': os.getenv('API_PREFIX', '/api'),
            'cors_origins': eval(os.getenv('CORS_ORIGINS', '["*"]')),
            'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
            'algorithm': os.getenv('ALGORITHM', 'HS256'),
            'access_token_expire_minutes': int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')),
            'max_chapter_length': int(os.getenv('MAX_CHAPTER_LENGTH', '3000')),
            'min_chapter_length': int(os.getenv('MIN_CHAPTER_LENGTH', '2000')),
            'choices_count': int(os.getenv('CHOICES_COUNT', '3'))
        }
        env_values.update(kwargs)
        super().__init__(**env_values)

settings = Settings()