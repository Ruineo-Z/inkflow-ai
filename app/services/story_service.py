from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models import Story, Chapter, Choice, StoryStyle, StoryStatus, ChoiceType, WorldView
from app.services.ai_service import ai_service
from app.services.worldview_service import WorldViewService
import uuid

class StoryService:
    def __init__(self, db: Session):
        self.db = db
        self.worldview_service = WorldViewService(db)
    
    def create_story(self, style: StoryStyle, title: str = None, user_id: str = None) -> Story:
        """创建新故事"""
        if not title:
            style_titles = {
                StoryStyle.XIANXIA: "修仙传奇",
                StoryStyle.WUXIA: "江湖风云",
                StoryStyle.SCIFI: "星际探索"
            }
            title = style_titles.get(style, "未知冒险")
        
        story = Story(
            title=title,
            style=style,
            status=StoryStatus.ACTIVE,
            current_chapter_number=0,
            user_id=user_id
        )
        
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        
        return story
    
    async def create_story_with_worldview(self, style: StoryStyle, title: str = None, user_id: str = None, story_theme: str = None) -> Dict[str, Any]:
        """创建新故事并生成世界观框架"""
        try:
            # 创建故事
            story = self.create_story(style, title, user_id)
            
            # 生成世界观框架
            worldview = await self.worldview_service.create_worldview(
                story_id=story.id,
                story_theme=story_theme
            )
            
            return {
                "story": story.to_dict(),
                "worldview": worldview.to_dict()
            }
            
        except Exception as e:
            # 如果世界观生成失败，删除已创建的故事
            if 'story' in locals():
                self.delete_story(story.id)
            raise e
    
    def get_story(self, story_id: uuid.UUID) -> Optional[Story]:
        """获取故事详情"""
        return self.db.query(Story).filter(Story.id == story_id).first()
    
    def get_all_stories(self) -> List[Story]:
        """获取所有故事列表"""
        return self.db.query(Story).order_by(Story.created_at.desc()).all()
    
    def get_user_stories(self, user_id: str) -> List[Story]:
        """获取指定用户的故事列表"""
        return self.db.query(Story).filter(
            Story.user_id == user_id
        ).order_by(Story.created_at.desc()).all()
    
    def get_story_chapters(self, story_id: uuid.UUID) -> List[Chapter]:
        """获取故事的所有章节"""
        return self.db.query(Chapter).filter(
            Chapter.story_id == story_id
        ).order_by(Chapter.chapter_number).all()
    
    def get_story_choices_history(self, story_id: uuid.UUID) -> List[Dict[str, Any]]:
        """获取故事的选择历史"""
        chapters = self.get_story_chapters(story_id)
        choices_history = []
        
        for chapter in chapters:
            selected_choice = self.db.query(Choice).filter(
                Choice.chapter_id == chapter.id,
                Choice.is_selected == True
            ).first()
            
            if selected_choice:
                choices_history.append({
                    "chapter_number": chapter.chapter_number,
                    "chapter_title": chapter.title,
                    "choice": selected_choice.to_dict()
                })
        
        return choices_history
    
    async def generate_first_chapter(self, story_id: uuid.UUID) -> Chapter:
        """基于世界观框架生成故事的第一章"""
        story = self.get_story(story_id)
        if not story:
            raise ValueError("故事不存在")
        
        # 获取世界观框架
        worldview = self.worldview_service.get_worldview(story_id)
        if not worldview:
            raise ValueError("故事缺少世界观框架，请先生成世界观")
        
        # 构建故事数据
        story_data = {
            "style": story.style.value,
            "title": story.title,
            "current_chapter_number": 1,
            "chapter_summaries": story.chapter_summaries or [],
            "character_info": story.character_info or {}
        }
        
        # 获取世界观上下文
        worldview_context = worldview.get_context_summary()
        
        # 生成章节内容
        chapter_result = await ai_service.generate_chapter(
            story_data, 
            worldview_context=worldview_context
        )
        
        # 创建章节
        chapter = Chapter(
            story_id=story.id,
            chapter_number=1,
            title=chapter_result["title"],
            content=chapter_result["content"],
            summary=chapter_result["content"][:200] + "..."  # 简单摘要
        )
        
        self.db.add(chapter)
        self.db.commit()  # 先提交章节以获取ID
        self.db.refresh(chapter)
        
        # 生成选择选项
        choices_text = await ai_service.generate_choices(
            chapter_result["content"], 
            story.style
        )
        
        for choice_text in choices_text:
            choice = Choice(
                chapter_id=chapter.id,
                choice_text=choice_text,
                choice_type=ChoiceType.AI_GENERATED
            )
            self.db.add(choice)
        
        # 更新故事状态
        story.current_chapter_number = 1
        story.chapter_summaries = [chapter.summary]
        
        self.db.commit()
        self.db.refresh(chapter)
        
        return chapter

    async def generate_first_chapter_stream(self, story_id: uuid.UUID):
        """流式生成故事的第一章"""
        try:
            story = self.get_story(story_id)
            if not story:
                yield {"type": "error", "message": "故事不存在"}
                return

            # 获取世界观框架
            worldview = self.worldview_service.get_worldview(story_id)
            if not worldview:
                yield {"type": "error", "message": "故事缺少世界观框架，请先生成世界观"}
                return

            # 构建故事数据
            story_data = {
                "style": story.style.value,
                "title": story.title,
                "current_chapter_number": 1,
                "chapter_summaries": story.chapter_summaries or [],
                "character_info": story.character_info or {}
            }

            # 获取世界观上下文
            worldview_context = worldview.get_context_summary()

            # 流式生成章节内容
            accumulated_content = ""
            chapter_title = ""

            async for chunk in ai_service.generate_chapter_stream(
                story_data,
                worldview_context=worldview_context
            ):
                if chunk["type"] == "title":
                    chapter_title = chunk["content"]
                    yield chunk
                elif chunk["type"] == "content":
                    accumulated_content += chunk["content"]
                    yield chunk
                elif chunk["type"] == "complete":
                    # 创建章节记录
                    chapter = Chapter(
                        story_id=story.id,
                        chapter_number=1,
                        title=chunk["title"],
                        content=chunk["content"],
                        summary=chunk["content"][:200] + "..."
                    )

                    self.db.add(chapter)
                    self.db.commit()  # 先提交章节以获取ID
                    self.db.refresh(chapter)

                    # 生成选择选项
                    try:
                        choices_text = await ai_service.generate_choices(
                            chunk["content"],
                            story.style
                        )

                        for choice_text in choices_text:
                            choice = Choice(
                                chapter_id=chapter.id,
                                choice_text=choice_text,
                                choice_type=ChoiceType.AI_GENERATED
                            )
                            self.db.add(choice)

                        # 更新故事状态
                        story.current_chapter_number = 1
                        story.chapter_summaries = [chapter.summary]

                        self.db.commit()
                        self.db.refresh(chapter)

                        # 发送完成信号，包含章节信息和选择选项
                        choices = self.get_chapter_choices(chapter.id)
                        yield {
                            "type": "complete",
                            "chapter": chapter.to_dict(),
                            "choices": [choice.to_dict() for choice in choices]
                        }

                    except Exception as e:
                        yield {"type": "error", "message": f"生成选择选项失败: {str(e)}"}

        except Exception as e:
            yield {"type": "error", "message": f"生成第一章失败: {str(e)}"}

    async def generate_next_chapter(self, story_id: uuid.UUID, selected_choice_id: uuid.UUID, custom_choice: str = None) -> Chapter:
        """基于世界观+章节总结+用户选择生成下一章"""
        story = self.get_story(story_id)
        if not story:
            raise ValueError("故事不存在")
        
        # 获取世界观框架
        worldview = self.worldview_service.get_worldview(story_id)
        if not worldview:
            raise ValueError("故事缺少世界观框架")
        
        # 处理用户选择
        choice_text = None
        if custom_choice:
            # 用户自定义选择
            choice_text = custom_choice
            # 创建自定义选择记录
            last_chapter = self.db.query(Chapter).filter(
                Chapter.story_id == story_id
            ).order_by(Chapter.chapter_number.desc()).first()
            
            if last_chapter:
                custom_choice_obj = Choice(
                    chapter_id=last_chapter.id,
                    choice_text=custom_choice,
                    choice_type=ChoiceType.USER_CUSTOM,
                    is_selected=True
                )
                self.db.add(custom_choice_obj)
        else:
            # AI生成的选择
            selected_choice = self.db.query(Choice).filter(
                Choice.id == selected_choice_id
            ).first()
            
            if not selected_choice:
                raise ValueError("选择不存在")
            
            # 标记选择为已选中
            selected_choice.is_selected = True
            choice_text = selected_choice.choice_text
        
        # 构建故事数据
        story_data = {
            "style": story.style.value,
            "title": story.title,
            "current_chapter_number": story.current_chapter_number + 1,
            "chapter_summaries": story.chapter_summaries or [],
            "character_info": story.character_info or {}
        }
        
        # 获取世界观上下文
        worldview_context = worldview.get_context_summary()
        
        # 生成新章节
        chapter_result = await ai_service.generate_chapter(
            story_data, 
            worldview_context=worldview_context,
            previous_choice=choice_text
        )
        
        # 创建章节
        new_chapter = Chapter(
            story_id=story.id,
            chapter_number=story.current_chapter_number + 1,
            title=chapter_result["title"],
            content=chapter_result["content"],
            summary=chapter_result["content"][:200] + "..."
        )
        
        self.db.add(new_chapter)
        self.db.commit()  # 先提交章节以获取ID
        self.db.refresh(new_chapter)
        
        # 生成新的选择选项
        choices_text = await ai_service.generate_choices(
            chapter_result["content"], 
            story.style
        )
        
        for choice_text in choices_text:
            choice = Choice(
                chapter_id=new_chapter.id,
                choice_text=choice_text,
                choice_type=ChoiceType.AI_GENERATED
            )
            self.db.add(choice)
        
        # 更新故事状态
        story.current_chapter_number += 1
        summaries = story.chapter_summaries or []
        summaries.append(new_chapter.summary)
        story.chapter_summaries = summaries
        
        self.db.commit()
        self.db.refresh(new_chapter)
        
        return new_chapter
    
    def get_chapter(self, chapter_id: uuid.UUID) -> Optional[Chapter]:
        """获取章节详情"""
        return self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    def get_chapter_choices(self, chapter_id: uuid.UUID) -> List[Choice]:
        """获取章节的选择选项"""
        return self.db.query(Choice).filter(
            Choice.chapter_id == chapter_id
        ).all()
    
    def delete_story(self, story_id: uuid.UUID) -> bool:
        """删除故事及其所有相关数据"""
        try:
            # 获取故事
            story = self.get_story(story_id)
            if not story:
                raise ValueError("故事不存在")
            
            # 由于模型中设置了cascade="all, delete-orphan"
            # 删除故事时会自动级联删除所有相关的章节和选择
            self.db.delete(story)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def generate_next_chapter_stream(self, story_id: uuid.UUID, selected_choice_id: uuid.UUID = None, custom_choice: str = None):
        """基于世界观+章节总结+用户选择流式生成下一章"""
        try:
            story = self.get_story(story_id)
            if not story:
                yield {"type": "error", "message": "故事不存在"}
                return
            
            # 获取世界观框架
            worldview = self.worldview_service.get_worldview(story_id)
            if not worldview:
                yield {"type": "error", "message": "故事缺少世界观框架"}
                return
            
            # 处理用户选择
            choice_text = None
            if custom_choice:
                # 用户自定义选择
                choice_text = custom_choice
                # 创建自定义选择记录
                last_chapter = self.db.query(Chapter).filter(
                    Chapter.story_id == story_id
                ).order_by(Chapter.chapter_number.desc()).first()
                
                if last_chapter:
                    custom_choice_obj = Choice(
                        chapter_id=last_chapter.id,
                        choice_text=custom_choice,
                        choice_type=ChoiceType.USER_CUSTOM,
                        is_selected=True
                    )
                    self.db.add(custom_choice_obj)
            else:
                # AI生成的选择
                if selected_choice_id:
                    selected_choice = self.db.query(Choice).filter(
                        Choice.id == selected_choice_id
                    ).first()
                    
                    if not selected_choice:
                        yield {"type": "error", "message": "选择不存在"}
                        return
                    
                    # 标记选择为已选中
                    selected_choice.is_selected = True
                    choice_text = selected_choice.choice_text
            
            # 构建故事数据
            story_data = {
                "style": story.style.value,
                "title": story.title,
                "current_chapter_number": story.current_chapter_number + 1,
                "chapter_summaries": story.chapter_summaries or [],
                "character_info": story.character_info or {}
            }
            
            # 获取世界观上下文
            worldview_context = worldview.get_context_summary()
            
            # 流式生成新章节
            accumulated_content = ""
            chapter_title = ""
            
            async for chunk in ai_service.generate_chapter_stream(
                story_data, 
                worldview_context=worldview_context,
                previous_choice=choice_text
            ):
                if chunk["type"] == "title":
                    chapter_title = chunk["content"]
                    yield chunk
                elif chunk["type"] == "content":
                    accumulated_content += chunk["content"]
                    yield chunk
                elif chunk["type"] == "complete":
                    # 创建章节记录
                    new_chapter = Chapter(
                        story_id=story.id,
                        chapter_number=story.current_chapter_number + 1,
                        title=chunk["title"],
                        content=chunk["content"],
                        summary=chunk["content"][:200] + "..."
                    )
                    
                    self.db.add(new_chapter)
                    self.db.commit()  # 先提交章节以获取ID
                    self.db.refresh(new_chapter)
                    
                    # 生成新的选择选项
                    try:
                        choices_text = await ai_service.generate_choices(
                            chunk["content"], 
                            story.style
                        )
                        
                        for choice_text in choices_text:
                            choice = Choice(
                                chapter_id=new_chapter.id,
                                choice_text=choice_text,
                                choice_type=ChoiceType.AI_GENERATED
                            )
                            self.db.add(choice)
                        
                        # 更新故事状态
                        story.current_chapter_number += 1
                        summaries = story.chapter_summaries or []
                        summaries.append(new_chapter.summary)
                        story.chapter_summaries = summaries
                        
                        self.db.commit()
                        self.db.refresh(new_chapter)
                        
                        # 发送完成信号，包含章节信息和选择选项
                        choices = self.get_chapter_choices(new_chapter.id)
                        yield {
                            "type": "complete",
                            "chapter": new_chapter.to_dict(),
                            "choices": [choice.to_dict() for choice in choices]
                        }
                        
                    except Exception as e:
                        yield {"type": "error", "message": f"生成选择选项失败: {str(e)}"}
                elif chunk["type"] == "error":
                    yield chunk
                    
        except Exception as e:
            self.db.rollback()
            yield {"type": "error", "message": f"生成章节失败: {str(e)}"}