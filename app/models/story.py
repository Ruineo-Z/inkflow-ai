from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum
from ..database.connection import Base

class StoryStyle(str, enum.Enum):
    XIANXIA = "修仙"
    WUXIA = "武侠"
    SCIFI = "科技"

class StoryStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    style = Column(Enum(StoryStyle), nullable=False)
    status = Column(Enum(StoryStatus), default=StoryStatus.ACTIVE)
    current_chapter_number = Column(Integer, default=0)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)  # 用户关联
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 故事状态数据（JSON格式存储）
    state_data = Column(JSON, default=dict)
    chapter_summaries = Column(JSON, default=list)
    character_info = Column(JSON, default=dict)
    
    # 关联关系
    user = relationship("User", back_populates="stories")
    chapters = relationship("Chapter", back_populates="story", cascade="all, delete-orphan")
    worldview = relationship("WorldView", back_populates="story", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story(id={self.id}, title='{self.title}', style='{self.style}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "style": self.style.value,
            "status": self.status.value,
            "current_chapter_number": self.current_chapter_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }