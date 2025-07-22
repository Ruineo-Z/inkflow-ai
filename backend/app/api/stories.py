from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models import StoryStyle
from app.services import StoryService

router = APIRouter(prefix="/stories", tags=["stories"])

# Pydantic模型
class CreateStoryRequest(BaseModel):
    style: StoryStyle
    title: str = None

class StoryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""

class ChapterResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""

@router.post("/", response_model=StoryResponse)
async def create_story(
    request: CreateStoryRequest,
    db: Session = Depends(get_db)
):
    """创建新故事"""
    try:
        story_service = StoryService(db)
        story = story_service.create_story(
            style=request.style,
            title=request.title
        )
        
        return StoryResponse(
            success=True,
            data=story.to_dict(),
            message="故事创建成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建故事失败: {str(e)}"
        )

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取故事详情"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )
        
        return StoryResponse(
            success=True,
            data=story.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取故事失败: {str(e)}"
        )

@router.get("/{story_id}/chapters")
async def get_story_chapters(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取故事章节列表"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )
        
        chapters = story_service.get_story_chapters(story_id)
        
        return {
            "success": True,
            "data": {
                "story_id": str(story_id),
                "chapters": [chapter.to_dict() for chapter in chapters]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节列表失败: {str(e)}"
        )

@router.post("/{story_id}/chapters", response_model=ChapterResponse)
async def generate_chapter(
    story_id: str,
    db: Session = Depends(get_db)
):
    """生成新章节"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )
        
        # 如果是第一章，生成首章
        if story.current_chapter_number == 0:
            chapter = await story_service.generate_first_chapter(story_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先做出选择再生成下一章"
            )
        
        return ChapterResponse(
            success=True,
            data=chapter.to_dict(),
            message="章节生成成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成章节失败: {str(e)}"
        )

@router.get("/{story_id}/choices")
async def get_story_choices_history(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取故事选择历史"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )
        
        choices_history = story_service.get_story_choices_history(story_id)
        
        return {
            "success": True,
            "data": {
                "story_id": str(story_id),
                "choices_history": choices_history
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取选择历史失败: {str(e)}"
        )