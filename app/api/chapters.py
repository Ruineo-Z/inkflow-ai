from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import ChoiceType, User
from app.models.responses import (
    SuccessResponse, ErrorResponse,
    ChapterResponse as ChapterResponseModel, STANDARD_RESPONSES,
    ChapterDetail, ChoicesListResponse, ChoiceDetail
)
from app.services import StoryService
from .auth import get_current_user

router = APIRouter(prefix="/chapters", tags=["章节"])

# Pydantic模型
class SubmitChoiceRequest(BaseModel):
    choice_id: Optional[str] = None
    custom_choice: Optional[str] = None

@router.get("/{chapter_id}",
           response_model=ChapterResponseModel,
           responses=STANDARD_RESPONSES)
async def get_chapter(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChapterResponseModel:
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

        # 转换为ChapterDetail模型
        chapter_detail = ChapterDetail(
            id=str(chapter.id),
            story_id=str(chapter.story_id),
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            content=chapter.content,
            summary=getattr(chapter, 'summary', None),
            created_at=chapter.created_at
        )

        return ChapterResponseModel(
            data=chapter_detail
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节失败: {str(e)}"
        )


@router.get("/{chapter_id}/choices",
           response_model=ChoicesListResponse,
           responses=STANDARD_RESPONSES)
async def get_chapter_choices(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChoicesListResponse:
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

        # 转换为ChoiceDetail模型
        choice_details = []
        for choice in choices:
            choice_detail = ChoiceDetail(
                id=str(choice.id),
                chapter_id=str(choice.chapter_id),
                choice_text=choice.choice_text,
                choice_number=getattr(choice, 'choice_number', 0),
                is_selected=getattr(choice, 'is_selected', False),
                created_at=choice.created_at
            )
            choice_details.append(choice_detail)

        return ChoicesListResponse.create(
            chapter_id=str(chapter_id),
            choices=choice_details
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取选择选项失败: {str(e)}"
        )

