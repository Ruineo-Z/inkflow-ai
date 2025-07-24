from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum
from ..database.connection import Base

class ChoiceType(str, enum.Enum):
    AI_GENERATED = "ai_generated"
    USER_CUSTOM = "user_custom"

class Choice(Base):
    __tablename__ = "choices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), nullable=False, index=True)
    choice_text = Column(Text, nullable=False)
    choice_type = Column(SQLEnum(ChoiceType), default=ChoiceType.AI_GENERATED)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # 关联关系
    chapter = relationship("Chapter", back_populates="choices")
    
    def __repr__(self):
        return f"<Choice(id={self.id}, chapter_id={self.chapter_id}, type={self.choice_type})>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "chapter_id": str(self.chapter_id),
            "text": self.choice_text,  # 前端期望的字段名是text
            "choice_type": self.choice_type.value,
            "is_selected": self.is_selected,
            "created_at": self.created_at.isoformat()
        }