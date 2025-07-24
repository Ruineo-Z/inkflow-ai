from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from ..database.connection import Base

class WorldView(Base):
    """世界观框架模型"""
    __tablename__ = "worldviews"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False, unique=True, index=True)
    
    # 世界观核心要素
    world_setting = Column(Text, nullable=False)  # 世界设定描述
    power_system = Column(Text)  # 力量体系（修炼/武功/科技等）
    social_structure = Column(Text)  # 社会结构
    geography = Column(Text)  # 地理环境
    history_background = Column(Text)  # 历史背景
    
    # 角色设定
    main_character = Column(JSON, default=dict)  # 主角设定
    supporting_characters = Column(JSON, default=list)  # 配角设定
    antagonists = Column(JSON, default=list)  # 反派设定
    
    # 故事框架
    main_plot = Column(Text)  # 主线剧情
    conflict_setup = Column(Text)  # 冲突设置
    story_themes = Column(JSON, default=list)  # 故事主题
    
    # 风格特色
    narrative_style = Column(Text)  # 叙述风格
    tone_atmosphere = Column(Text)  # 基调氛围
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    story = relationship("Story", back_populates="worldview")
    
    def __repr__(self):
        return f"<WorldView(id={self.id}, story_id={self.story_id})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "story_id": str(self.story_id),
            "world_setting": self.world_setting,
            "power_system": self.power_system,
            "social_structure": self.social_structure,
            "geography": self.geography,
            "history_background": self.history_background,
            "main_character": self.main_character,
            "supporting_characters": self.supporting_characters,
            "antagonists": self.antagonists,
            "main_plot": self.main_plot,
            "conflict_setup": self.conflict_setup,
            "story_themes": self.story_themes,
            "narrative_style": self.narrative_style,
            "tone_atmosphere": self.tone_atmosphere,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_context_summary(self) -> str:
        """获取世界观的上下文摘要，用于AI生成"""
        context = f"世界设定：{self.world_setting}\n"
        
        if self.power_system:
            context += f"力量体系：{self.power_system}\n"
        
        if self.social_structure:
            context += f"社会结构：{self.social_structure}\n"
        
        if self.geography:
            context += f"地理环境：{self.geography}\n"
        
        if self.history_background:
            context += f"历史背景：{self.history_background}\n"
        
        if self.main_character:
            context += f"主角设定：{self.main_character.get('name', '未知')} - {self.main_character.get('description', '')}\n"
        
        if self.main_plot:
            context += f"主线剧情：{self.main_plot}\n"
        
        if self.conflict_setup:
            context += f"冲突设置：{self.conflict_setup}\n"
        
        if self.narrative_style:
            context += f"叙述风格：{self.narrative_style}\n"
        
        if self.tone_atmosphere:
            context += f"基调氛围：{self.tone_atmosphere}\n"
        
        return context