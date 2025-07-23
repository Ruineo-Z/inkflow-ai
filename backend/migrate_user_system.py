#!/usr/bin/env python3
"""
数据库迁移脚本：添加用户管理系统

此脚本将：
1. 创建用户表
2. 为故事表添加用户关联字段
3. 为现有故事创建默认用户
"""

import sys
import os
from sqlalchemy import create_engine, text, Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import uuid
import secrets
import string

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.database.connection import Base
from app.models import User, Story

def generate_user_id():
    """生成12位随机用户ID"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(12))

def migrate_database():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. 创建所有表（包括新的用户表）
        print("1. 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        # 2. 检查是否需要添加user_id列到stories表
        print("2. 检查stories表结构...")
        
        # 检查stories表是否已有user_id列（PostgreSQL语法）
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'stories' AND table_schema = 'public'
        """))
        columns = [row[0] for row in result.fetchall()]
        
        if 'user_id' not in columns:
            print("   添加user_id列到stories表...")
            session.execute(text("ALTER TABLE stories ADD COLUMN user_id VARCHAR(36)"))
            session.commit()
        else:
            print("   stories表已包含user_id列")
        
        # 3. 创建默认用户（如果不存在）
        print("3. 检查默认用户...")
        default_user = session.query(User).filter_by(username="default_user").first()
        
        if not default_user:
            print("   创建默认用户...")
            default_user = User(
                username="default_user",
                user_id=generate_user_id()
            )
            session.add(default_user)
            session.commit()
            session.refresh(default_user)
            print(f"   默认用户已创建: {default_user.username} (ID: {default_user.user_id})")
        else:
            print(f"   默认用户已存在: {default_user.username} (ID: {default_user.user_id})")
        
        # 4. 为现有的没有用户关联的故事分配默认用户
        print("4. 更新现有故事的用户关联...")
        stories_without_user = session.query(Story).filter(Story.user_id.is_(None)).all()
        
        if stories_without_user:
            print(f"   找到 {len(stories_without_user)} 个没有用户关联的故事")
            for story in stories_without_user:
                story.user_id = default_user.id
                print(f"   故事 '{story.title}' 已关联到默认用户")
            
            session.commit()
            print(f"   已更新 {len(stories_without_user)} 个故事的用户关联")
        else:
            print("   所有故事都已有用户关联")
        
        print("\n数据库迁移完成！")
        print(f"默认用户登录ID: {default_user.user_id}")
        print("\n注意：")
        print("1. 现有的所有故事已关联到默认用户")
        print("2. 用户可以使用默认用户ID登录查看现有故事")
        print("3. 新用户注册后将只能看到自己创建的故事")
        
    except Exception as e:
        print(f"迁移过程中出现错误: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_database()