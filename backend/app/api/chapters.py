from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import ChoiceType
from app.services import StoryService

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