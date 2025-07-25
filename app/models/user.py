from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import secrets
import string
from ..database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), nullable=False, unique=True)
    user_id = Column(String(12), nullable=False, unique=True)  # 用户登录ID
    password_hash = Column(String(255), nullable=False)  # 密码哈希
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, username, password_hash=None, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.password_hash = password_hash
        if not self.user_id:
            self.user_id = self.generate_user_id()
    
    @staticmethod
    def generate_user_id():
        """生成12位随机用户ID"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(12))
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', user_id='{self.user_id}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_public_dict(self):
        """返回公开信息，不包含敏感数据"""
        return {
            "username": self.username,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat()
        }