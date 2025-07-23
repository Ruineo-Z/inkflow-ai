from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import asyncio

from app.database import get_db
from app.models import ChoiceType, User
from app.services import StoryService
from .auth import get_current_user

router = APIRouter(prefix="/chapters", tags=["chapters"])

# Pydantic模型
class ChapterResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""

class SubmitChoiceRequest(BaseModel):
    choice_id: Optional[str] = None
    custom_choice: Optional[str] = None

class NextChapterResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""

@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取章节详情"""
    try:
        story_service = StoryService(db)
        chapter = story_service.get_chapter(chapter_id)
        
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        
        # 检查用户权限
        story = story_service.get_story(chapter.story_id)
        if story and story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此章节"
            )
        
        return ChapterResponse(
            success=True,
            data=chapter.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节失败: {str(e)}"
        )

@router.post("/{chapter_id}/choices", response_model=NextChapterResponse)
async def submit_choice(
    chapter_id: str,
    request: SubmitChoiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交用户选择并生成下一章"""
    try:
        story_service = StoryService(db)
        chapter = story_service.get_chapter(chapter_id)
        
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        
        # 检查用户权限
        story = story_service.get_story(chapter.story_id)
        if story and story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此章节"
            )
        
        # 验证选择参数
        if not request.choice_id and not request.custom_choice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供选择ID或自定义选择内容"
            )
        
        if request.choice_id and request.custom_choice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能同时提供选择ID和自定义选择内容"
            )
        
        # 生成下一章
        next_chapter = await story_service.generate_next_chapter(
            story_id=chapter.story_id,
            selected_choice_id=request.choice_id,
            custom_choice=request.custom_choice
        )
        
        return NextChapterResponse(
            success=True,
            data=next_chapter.to_dict(),
            message="选择提交成功，下一章已生成"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交选择失败: {str(e)}"
        )

@router.get("/{chapter_id}/choices")
async def get_chapter_choices(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取章节的选择选项"""
    try:
        story_service = StoryService(db)
        chapter = story_service.get_chapter(chapter_id)
        
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        
        # 检查用户权限
        story = story_service.get_story(chapter.story_id)
        if story and story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此章节"
            )
        
        choices = story_service.get_chapter_choices(chapter_id)
        
        return {
            "success": True,
            "data": {
                "chapter_id": str(chapter_id),
                "choices": [choice.to_dict() for choice in choices]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取选择选项失败: {str(e)}"
        )

@router.post("/stream/{chapter_id}/choices")
async def submit_choice_stream(
    chapter_id: str,
    request: SubmitChoiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交用户选择并流式生成下一章"""
    async def generate_stream():
        try:
            story_service = StoryService(db)
            chapter = story_service.get_chapter(chapter_id)
            
            if not chapter:
                yield f"data: {json.dumps({'type': 'error', 'message': '章节不存在'})}\n\n"
                return
            
            # 检查用户权限
            story = story_service.get_story(chapter.story_id)
            if story and story.user_id != current_user.id:
                yield f"data: {json.dumps({'type': 'error', 'message': '无权访问此章节'})}\n\n"
                return
            
            # 验证选择参数
            if not request.choice_id and not request.custom_choice:
                yield f"data: {json.dumps({'type': 'error', 'message': '必须提供选择ID或自定义选择内容'})}\n\n"
                return
            
            if request.choice_id and request.custom_choice:
                yield f"data: {json.dumps({'type': 'error', 'message': '不能同时提供选择ID和自定义选择内容'})}\n\n"
                return
            
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '开始生成章节...'})}\n\n"
            
            # 流式生成下一章
            async for chunk in story_service.generate_next_chapter_stream(
                story_id=chapter.story_id,
                selected_choice_id=request.choice_id,
                custom_choice=request.custom_choice
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)  # 小延迟确保流畅传输
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'生成章节失败: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )