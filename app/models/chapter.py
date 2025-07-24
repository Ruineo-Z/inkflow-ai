from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from ..database.connection import Base

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False, index=True)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    story = relationship("Story", back_populates="chapters")
    choices = relationship("Choice", back_populates="chapter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, story_id={self.story_id}, number={self.chapter_number})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "story_id": str(self.story_id),
            "chapter_number": self.chapter_number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "choices": [choice.to_dict() for choice in self.choices] if self.choices else []
        }