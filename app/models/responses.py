"""
标准API响应模型
统一所有API接口的响应格式
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseAPIResponse(BaseModel):
    """API基础响应格式"""
    success: bool
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def model_dump(self, **kwargs):
        """重写model_dump以处理datetime序列化"""
        data = super().model_dump(**kwargs)
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


class SuccessResponse(BaseAPIResponse):
    """成功响应格式"""
    success: bool = True
    data: Any


class ErrorResponse(BaseAPIResponse):
    """错误响应格式"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


class ListResponse(BaseAPIResponse):
    """列表数据响应格式"""
    success: bool = True
    data: List[Any]
    pagination: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create(cls, data: List[Any], total: int, page: int = 1, page_size: int = 20, **kwargs):
        """创建列表响应"""
        return cls(
            data=data,
            pagination={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            },
            **kwargs
        )


# 具体业务响应模型
class StoryDetail(BaseModel):
    """故事详情模型"""
    id: str
    title: str
    genre: str
    style: str
    description: Optional[str] = None
    status: str
    current_chapter_number: int
    chapter_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryResponse(BaseModel):
    """故事响应模型（兼容性保留）"""
    id: str
    title: str
    genre: str
    style: str
    description: Optional[str] = None
    status: str
    current_chapter_number: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoriesListResponse(SuccessResponse):
    """故事列表响应"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "stories": [],
        "total": 0,
        "page": 1,
        "page_size": 20
    })

    @classmethod
    def create(cls, stories: List[StoryDetail], total: int, page: int = 1, page_size: int = 20, **kwargs):
        """创建故事列表响应"""
        return cls(
            data={
                "stories": [story.dict() for story in stories],
                "total": total,
                "page": page,
                "page_size": page_size
            },
            message="获取故事列表成功",
            **kwargs
        )


class ChapterDetail(BaseModel):
    """章节详情模型"""
    id: str
    story_id: str
    chapter_number: int
    title: str
    content: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChapterResponse(SuccessResponse):
    """单个章节响应模型"""
    data: ChapterDetail


class ChaptersListResponse(SuccessResponse):
    """章节列表响应模型"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "story_id": "",
        "chapters": []
    })

    @classmethod
    def create(cls, story_id: str, chapters: List[ChapterDetail], **kwargs):
        """创建章节列表响应"""
        return cls(
            data={
                "story_id": story_id,
                "chapters": [chapter.dict() for chapter in chapters]
            },
            message="获取章节列表成功",
            **kwargs
        )


class ChoiceDetail(BaseModel):
    """选择项详情模型"""
    id: str
    chapter_id: str
    choice_text: str
    choice_number: int
    is_selected: bool = False
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChoicesListResponse(SuccessResponse):
    """选择列表响应模型"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "chapter_id": "",
        "choices": []
    })

    @classmethod
    def create(cls, chapter_id: str, choices: List[ChoiceDetail], **kwargs):
        """创建选择列表响应"""
        return cls(
            data={
                "chapter_id": chapter_id,
                "choices": [choice.dict() for choice in choices]
            },
            message="获取选择列表成功",
            **kwargs
        )


class StoryChoicesHistoryResponse(SuccessResponse):
    """故事选择历史响应模型"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "story_id": "",
        "choices_history": []
    })

    @classmethod
    def create(cls, story_id: str, choices_history: List[Dict], **kwargs):
        """创建故事选择历史响应"""
        return cls(
            data={
                "story_id": story_id,
                "choices_history": choices_history
            },
            message="获取选择历史成功",
            **kwargs
        )


class ChapterChoicesResponse(SuccessResponse):
    """章节选择响应"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "chapter": None,
        "choices": []
    })


class UserResponse(BaseModel):
    """用户响应模型"""
    username: str
    user_id: str
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuthResponse(SuccessResponse):
    """认证响应模型"""
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "user": None,
        "token": None
    })


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    version: str
    services: Dict[str, str]

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "redis": "connected"
                }
            }
        }


class RootResponse(BaseModel):
    """根路径响应模型"""
    message: str
    version: str
    status: str

    class Config:
        schema_extra = {
            "example": {
                "message": "AI Interactive Novel API",
                "version": "1.0.0",
                "status": "running"
            }
        }


# 标准HTTP状态码响应定义
STANDARD_RESPONSES = {
    200: {"model": SuccessResponse, "description": "请求成功"},
    400: {"model": ErrorResponse, "description": "请求参数错误"},
    401: {"model": ErrorResponse, "description": "未授权访问"},
    403: {"model": ErrorResponse, "description": "权限不足"},
    404: {"model": ErrorResponse, "description": "资源不存在"},
    422: {"model": ErrorResponse, "description": "数据验证失败"},
    500: {"model": ErrorResponse, "description": "服务器内部错误"}
}
