from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models import Story, Chapter, Choice, StoryStyle, StoryStatus, ChoiceType
from app.services.ai_service import ai_service
import uuid

class StoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_story(self, style: StoryStyle, title: str = None) -> Story:
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
            current_chapter_number=0
        )
        
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        
        return story
    
    def get_story(self, story_id: uuid.UUID) -> Optional[Story]:
        """获取故事详情"""
        return self.db.query(Story).filter(Story.id == story_id).first()
    
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
        """生成故事的第一章"""
        story = self.get_story(story_id)
        if not story:
            raise ValueError("故事不存在")
        
        # 构建故事数据
        story_data = {
            "style": story.style.value,
            "title": story.title,
            "current_chapter_number": 1,
            "chapter_summaries": story.chapter_summaries or [],
            "character_info": story.character_info or {}
        }
        
        # 生成章节内容
        chapter_result = await ai_service.generate_chapter(story_data)
        
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
    
    async def generate_next_chapter(self, story_id: uuid.UUID, selected_choice_id: uuid.UUID, custom_choice: str = None) -> Chapter:
        """基于用户选择生成下一章"""
        story = self.get_story(story_id)
        if not story:
            raise ValueError("故事不存在")
        
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
        
        # 生成新章节
        chapter_result = await ai_service.generate_chapter(story_data, choice_text)
        
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