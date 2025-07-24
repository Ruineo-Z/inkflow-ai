#!/usr/bin/env python3
"""
数据库迁移脚本：添加WorldView表

运行方式：
python migrate_worldview.py
"""

import sqlite3
import os

def migrate_worldview():
    """添加WorldView表"""
    print("开始数据库迁移：添加WorldView表...")
    
    try:
        # 数据库文件路径
        db_path = "ai_novel.db"
        
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建WorldView表的SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS worldviews (
            id TEXT PRIMARY KEY,
            story_id TEXT NOT NULL,
            world_setting TEXT,
            power_system TEXT,
            social_structure TEXT,
            geography TEXT,
            history_background TEXT,
            main_character TEXT,
            supporting_characters TEXT,
            antagonists TEXT,
            main_plot TEXT,
            conflict_setup TEXT,
            story_themes TEXT,
            narrative_style TEXT,
            tone_atmosphere TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories (id) ON DELETE CASCADE
        );
        """
        
        # 执行创建表语句
        cursor.execute(create_table_sql)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worldviews_story_id ON worldviews(story_id);")
        
        # 提交更改
        conn.commit()
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worldviews';")
        if cursor.fetchone():
            print("✅ WorldView表创建成功！")
        else:
            print("❌ WorldView表创建失败")
            return False
        
        # 关闭连接
        conn.close()
        
        print("🎉 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

if __name__ == "__main__":
    success = migrate_worldview()
    if success:
        print("\n现在可以使用新的世界观功能了！")
        print("\n新功能包括：")
        print("- 创建故事时自动生成世界观框架")
        print("- 基于世界观生成第一章")
        print("- 后续章节基于世界观+前章总结+用户选择生成")
        print("- 支持流式输出章节内容")
    else:
        print("\n迁移失败，请检查错误信息并重试。")
        exit(1)