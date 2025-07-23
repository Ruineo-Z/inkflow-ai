#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('DATABASE_URL', 'postgresql://admin:admin@localhost:5432/ai_novel_db')
os.environ.setdefault('GEMINI_API_KEY', 'AIzaSyBnllTxBgQY6CIunsWLthUrOK0KTrVcFfU')
os.environ.setdefault('GEMINI_MODEL', 'gemini-2.5-flash')

from app.services.ai_service import AIService
from app.models.story import StoryStyle

async def test_gemini_api():
    """测试Gemini API连接和生成功能"""
    print("开始测试Gemini API...")
    
    # 创建AI服务实例
    ai_service = AIService()
    
    # 检查API密钥配置
    if not ai_service.model:
        print("❌ Gemini API未正确配置")
        return False
    
    print("✅ Gemini API配置正常")
    
    # 测试章节生成
    try:
        print("\n测试章节生成...")
        story_data = {
            'title': '测试故事',
            'style': '修仙',
            'current_chapter_number': 1,
            'chapter_summaries': [],
            'character_info': {}
        }
        
        result = await ai_service.generate_chapter(story_data)
        print(f"✅ 章节生成成功:")
        print(f"标题: {result['title']}")
        print(f"内容长度: {len(result['content'])} 字符")
        print(f"内容预览: {result['content'][:100]}...")
        
        # 测试选择生成
        print("\n测试选择生成...")
        choices = await ai_service.generate_choices(result['content'], StoryStyle.XIANXIA)
        print(f"✅ 选择生成成功:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_api())
    if success:
        print("\n🎉 Gemini API测试通过！")
    else:
        print("\n💥 Gemini API测试失败！")
        sys.exit(1)