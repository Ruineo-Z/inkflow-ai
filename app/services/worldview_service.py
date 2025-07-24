from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models import WorldView, Story, StoryStyle
from app.services.ai_service import ai_service
import uuid

class WorldViewService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_worldview(self, story_id: str, story_theme: str = None) -> WorldView:
        """为故事创建世界观框架"""
        # 获取故事信息
        story = self.db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError("故事不存在")
        
        # 检查是否已存在世界观
        existing_worldview = self.db.query(WorldView).filter(
            WorldView.story_id == story_id
        ).first()
        
        if existing_worldview:
            raise ValueError("该故事已存在世界观框架")
        
        try:
            # 使用AI生成世界观框架
            worldview_data = await ai_service.generate_worldview(
                story_title=story.title,
                story_style=story.style,
                story_theme=story_theme
            )
            
            # 创建世界观记录
            worldview = WorldView(
                story_id=story_id,
                world_setting=worldview_data.get('world_setting', ''),
                power_system=worldview_data.get('power_system', ''),
                social_structure=worldview_data.get('social_structure', ''),
                geography=worldview_data.get('geography', ''),
                history_background=worldview_data.get('history_background', ''),
                main_character=worldview_data.get('main_character', {}),
                supporting_characters=worldview_data.get('supporting_characters', []),
                antagonists=worldview_data.get('antagonists', []),
                main_plot=worldview_data.get('main_plot', ''),
                conflict_setup=worldview_data.get('conflict_setup', ''),
                story_themes=worldview_data.get('story_themes', []),
                narrative_style=worldview_data.get('narrative_style', ''),
                tone_atmosphere=worldview_data.get('tone_atmosphere', '')
            )
            
            self.db.add(worldview)
            self.db.commit()
            self.db.refresh(worldview)
            
            return worldview
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"生成世界观失败: {str(e)}")
    
    def get_worldview(self, story_id: str) -> Optional[WorldView]:
        """获取故事的世界观框架"""
        return self.db.query(WorldView).filter(
            WorldView.story_id == story_id
        ).first()
    
    def get_worldview_by_id(self, worldview_id: str) -> Optional[WorldView]:
        """根据ID获取世界观"""
        return self.db.query(WorldView).filter(
            WorldView.id == worldview_id
        ).first()
    
    async def update_worldview(self, worldview_id: str, update_data: Dict[str, Any]) -> WorldView:
        """更新世界观框架"""
        worldview = self.get_worldview_by_id(worldview_id)
        if not worldview:
            raise ValueError("世界观不存在")
        
        try:
            # 更新字段
            for field, value in update_data.items():
                if hasattr(worldview, field):
                    setattr(worldview, field, value)
            
            self.db.commit()
            self.db.refresh(worldview)
            
            return worldview
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新世界观失败: {str(e)}")
    
    def delete_worldview(self, worldview_id: str) -> bool:
        """删除世界观框架"""
        try:
            worldview = self.get_worldview_by_id(worldview_id)
            if not worldview:
                raise ValueError("世界观不存在")
            
            self.db.delete(worldview)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def regenerate_worldview(self, story_id: str, story_theme: str = None) -> WorldView:
        """重新生成世界观框架"""
        # 删除现有世界观
        existing_worldview = self.get_worldview(story_id)
        if existing_worldview:
            self.delete_worldview(existing_worldview.id)
        
        # 创建新的世界观
        return await self.create_worldview(story_id, story_theme)
    
    def add_character(self, worldview_id: str, character_data: Dict[str, Any], character_type: str = 'supporting') -> WorldView:
        """添加角色到世界观"""
        worldview = self.get_worldview_by_id(worldview_id)
        if not worldview:
            raise ValueError("世界观不存在")
        
        try:
            if character_type == 'supporting':
                characters = worldview.supporting_characters or []
                characters.append(character_data)
                worldview.supporting_characters = characters
            elif character_type == 'antagonist':
                antagonists = worldview.antagonists or []
                antagonists.append(character_data)
                worldview.antagonists = antagonists
            else:
                raise ValueError("不支持的角色类型")
            
            self.db.commit()
            self.db.refresh(worldview)
            
            return worldview
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"添加角色失败: {str(e)}")
    
    def update_main_character(self, worldview_id: str, character_data: Dict[str, Any]) -> WorldView:
        """更新主角信息"""
        worldview = self.get_worldview_by_id(worldview_id)
        if not worldview:
            raise ValueError("世界观不存在")
        
        try:
            # 合并主角数据
            main_character = worldview.main_character or {}
            main_character.update(character_data)
            worldview.main_character = main_character
            
            self.db.commit()
            self.db.refresh(worldview)
            
            return worldview
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"更新主角失败: {str(e)}")