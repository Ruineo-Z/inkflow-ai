from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models import StoryStyle, User
from app.models.responses import (
    SuccessResponse, ErrorResponse, StoriesListResponse,
    StoryDetail, StoryResponse as StoryResponseModel, STANDARD_RESPONSES,
    ChaptersListResponse, ChapterDetail, StoryChoicesHistoryResponse
)
from app.services import StoryService, WorldViewService
from .auth import get_current_user

router = APIRouter(prefix="/stories", tags=["故事"])

# Pydantic模型
class CreateStoryRequest(BaseModel):
    style: StoryStyle
    title: str = None
    theme: str = None  # 小说主题，用于生成世界观

class StoryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""



@router.get("/",
           response_model=StoriesListResponse,
           responses=STANDARD_RESPONSES)
async def get_all_stories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StoriesListResponse:
    """获取所有故事列表"""
    try:
        story_service = StoryService(db)
        stories = story_service.get_user_stories(current_user.id)

        # 转换为详细故事模型
        story_details = []
        for story in stories:
            # 获取章节数量
            chapters = story_service.get_story_chapters(story.id)
            story_detail = StoryDetail(
                id=story.id,
                title=story.title,
                genre=story.style.value if story.style else "",  # 使用style作为genre
                style=story.style.value if story.style else "",
                description=getattr(story, 'description', ''),
                status=story.status.value if story.status else "active",
                current_chapter_number=story.current_chapter_number,
                chapter_count=len(chapters),
                created_at=story.created_at,
                updated_at=story.updated_at
            )
            story_details.append(story_detail)

        return StoriesListResponse.create(
            stories=story_details,
            total=len(story_details)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取故事列表失败: {str(e)}"
        )

@router.post("/",
            response_model=SuccessResponse,
            responses=STANDARD_RESPONSES)
async def create_story(
    request: CreateStoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """创建新故事并生成世界观框架"""
    try:
        story_service = StoryService(db)

        # 如果提供了主题，使用新的世界观生成流程
        if request.theme:
            story = await story_service.create_story_with_worldview(
                style=request.style,
                title=request.title,
                story_theme=request.theme,
                user_id=current_user.id
            )
        else:
            # 兼容旧的创建方式
            story = story_service.create_story(
                style=request.style,
                title=request.title,
                user_id=current_user.id
            )

        return SuccessResponse(
            data=story.to_dict(),
            message="故事创建成功" + ("，世界观已生成" if request.theme else "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建故事失败: {str(e)}"
        )

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    current_user: User = Depends(get_current_user),
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
        
        # 检查用户权限
        if story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此故事"
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

@router.get("/{story_id}/chapters",
           response_model=ChaptersListResponse,
           responses=STANDARD_RESPONSES)
async def get_story_chapters(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChaptersListResponse:
    """获取故事章节列表"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)

        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )

        # 检查用户权限
        if story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此故事"
            )

        chapters = story_service.get_story_chapters(story_id)

        # 转换为ChapterDetail模型
        chapter_details = []
        for chapter in chapters:
            chapter_detail = ChapterDetail(
                id=str(chapter.id),
                story_id=str(chapter.story_id),
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                content=chapter.content,
                summary=getattr(chapter, 'summary', None),
                created_at=chapter.created_at
            )
            chapter_details.append(chapter_detail)

        return ChaptersListResponse.create(
            story_id=str(story_id),
            chapters=chapter_details
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节列表失败: {str(e)}"
        )


@router.post("/{story_id}/chapters/stream")
async def generate_chapter_stream(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式生成新章节（第一章）"""
    from fastapi.responses import StreamingResponse
    import json
    import asyncio

    async def generate_stream():
        try:
            story_service = StoryService(db)
            story = story_service.get_story(story_id)

            if not story:
                yield f"data: {json.dumps({'type': 'error', 'message': '故事不存在'})}\n\n"
                return

            # 检查用户权限
            if story.user_id != current_user.id:
                yield f"data: {json.dumps({'type': 'error', 'message': '无权访问此故事'})}\n\n"
                return

            # 只允许生成第一章
            if story.current_chapter_number != 0:
                yield f"data: {json.dumps({'type': 'error', 'message': '请先做出选择再生成下一章'})}\n\n"
                return

            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '开始生成第一章...'})}\n\n"

            # 流式生成第一章
            async for chunk in story_service.generate_first_chapter_stream(story_id):
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

@router.get("/{story_id}/choices",
           response_model=StoryChoicesHistoryResponse,
           responses=STANDARD_RESPONSES)
async def get_story_choices_history(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> StoryChoicesHistoryResponse:
    """获取故事选择历史"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)

        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )

        # 检查用户权限
        if story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此故事"
            )

        choices_history = story_service.get_story_choices_history(story_id)

        return StoryChoicesHistoryResponse.create(
            story_id=str(story_id),
            choices_history=choices_history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取选择历史失败: {str(e)}"
        )

@router.delete("/{story_id}", response_model=StoryResponse)
async def delete_story(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除故事及其所有相关数据"""
    try:
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在"
            )
        
        # 检查用户权限
        if story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此故事"
            )
        
        # 删除故事
        story_service.delete_story(story_id)
        
        return StoryResponse(
            success=True,
            data={"story_id": str(story_id)},
            message="故事删除成功"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除故事失败: {str(e)}"
        )

# 世界观相关API
@router.get("/{story_id}/worldview")
async def get_story_worldview(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取故事的世界观框架"""
    try:
        worldview_service = WorldViewService(db)
        worldview = worldview_service.get_worldview(story_id)
        
        if not worldview:
            return {
                "success": False,
                "data": None,
                "message": "该故事暂无世界观框架"
            }
        
        return {
            "success": True,
            "data": worldview.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取世界观失败: {str(e)}"
        )

@router.post("/{story_id}/worldview")
async def create_worldview(
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """为故事创建世界观框架"""
    try:
        # 验证故事存在且属于当前用户
        story_service = StoryService(db)
        story = story_service.get_story(story_id)
        if not story or story.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="故事不存在或无权限访问"
            )

        worldview_service = WorldViewService(db)
        worldview = await worldview_service.create_worldview(
            story_id=story_id
        )

        return {
            "success": True,
            "data": worldview.to_dict(),
            "message": "世界观创建成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建世界观失败: {str(e)}"
        )

