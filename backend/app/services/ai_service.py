import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
from app.config import settings
from app.models import StoryStyle

class AIService:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        else:
            self.model = None
    
    def _get_style_prompt(self, style: StoryStyle) -> str:
        """根据故事风格获取对应的prompt模板"""
        prompts = {
            StoryStyle.XIANXIA: """
你是一位专业的修仙小说作家。请创作一个修仙风格的故事章节，包含以下元素：
- 古典仙侠世界观，包含修炼体系、门派、法宝等元素
- 生动的人物描写和对话
- 引人入胜的情节发展
- 适当的悬念和冲突
章节长度应在2000-3000字之间。
""",
            StoryStyle.WUXIA: """
你是一位专业的武侠小说作家。请创作一个武侠风格的故事章节，包含以下元素：
- 江湖世界观，包含武功、门派、恩怨情仇
- 侠义精神和江湖道义
- 精彩的武打场面描写
- 人物性格鲜明，对话生动
章节长度应在2000-3000字之间。
""",
            StoryStyle.SCIFI: """
你是一位专业的科幻小说作家。请创作一个科技风格的故事章节，包含以下元素：
- 未来科技世界观，包含先进科技、太空探索、AI文明
- 科学幻想与人文思考的结合
- 紧张刺激的情节发展
- 对未来社会的深度思考
章节长度应在2000-3000字之间。
"""
        }
        return prompts.get(style, prompts[StoryStyle.XIANXIA])
    
    def _build_context(self, story_data: Dict[str, Any], previous_choice: str = None) -> str:
        """构建故事上下文"""
        context = f"故事风格：{story_data.get('style', '')}\n"
        context += f"故事标题：{story_data.get('title', '')}\n"
        
        # 添加章节摘要
        if story_data.get('chapter_summaries'):
            context += "\n之前的故事情节：\n"
            for i, summary in enumerate(story_data['chapter_summaries'], 1):
                context += f"第{i}章：{summary}\n"
        
        # 添加角色信息
        if story_data.get('character_info'):
            context += "\n主要角色：\n"
            for name, info in story_data['character_info'].items():
                context += f"{name}：{info}\n"
        
        # 添加用户选择
        if previous_choice:
            context += f"\n用户的选择：{previous_choice}\n"
        
        return context
    
    async def generate_chapter(self, story_data: Dict[str, Any], previous_choice: str = None) -> Dict[str, Any]:
        """生成章节内容"""
        print(f"生成章节 - 故事ID: {story_data.get('title', 'Unknown')}, 章节: {story_data.get('current_chapter_number', 1)}")
        
        # 使用真实AI生成
        if not self.model:
            print("Gemini API未配置，使用模拟数据")
            return self._generate_mock_chapter(story_data, previous_choice)
        
        try:
            style = StoryStyle(story_data['style'])
            style_prompt = self._get_style_prompt(style)
            context = self._build_context(story_data, previous_choice)
            
            prompt = f"""{style_prompt}

{context}

请基于以上信息，创作下一章节的内容。要求：
1. 章节内容要连贯自然，与之前的情节呼应
2. 如果有用户选择，要体现选择的影响
3. 在章节结尾设置适当的悬念
4. 返回格式为JSON，包含title（章节标题）和content（章节内容）

示例格式：
{{
    "title": "章节标题",
    "content": "章节内容..."
}}"""
            
            response = await self.model.generate_content_async(prompt)
            
            # 解析AI响应
            content = response.text
            
            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*"title"[^{}]*"content"[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 如果无法解析JSON，手动构建结果
            lines = content.split('\n')
            title = f"第{story_data.get('current_chapter_number', 1)}章"
            
            return {
                "title": title,
                "content": content.strip()
            }
            
        except Exception as e:
            print(f"AI生成章节失败: {e}")
            return self._generate_mock_chapter(story_data, previous_choice)
    
    async def generate_choices(self, chapter_content: str, story_style: StoryStyle) -> List[str]:
        """生成选择选项"""
        print(f"生成选择 - 风格: {story_style.value}")
        
        # 使用真实AI生成
        if not self.model:
            print("Gemini API未配置，使用模拟数据")
            return self._generate_mock_choices(story_style)
        
        try:
            prompt = f"""
基于以下章节内容，生成3个不同的选择选项，让读者决定故事的发展方向。

章节内容：
{chapter_content}

要求：
1. 3个选择要有明显的差异，代表不同的发展方向
2. 选择要符合{story_style.value}风格
3. 每个选择都要简洁明了，不超过30字
4. 返回JSON格式的数组

示例格式：
["选择1", "选择2", "选择3"]
"""
            
            response = await self.model.generate_content_async(prompt)
            content = response.text
            
            # 尝试解析JSON数组
            json_match = re.search(r'\[[^\[\]]*\]', content)
            if json_match:
                try:
                    choices = json.loads(json_match.group())
                    if isinstance(choices, list) and len(choices) >= 3:
                        return choices[:3]
                except json.JSONDecodeError:
                    pass
            
            # 如果解析失败，返回模拟选择
            return self._generate_mock_choices(story_style)
            
        except Exception as e:
            print(f"AI生成选择失败: {e}")
            return self._generate_mock_choices(story_style)
    
    def _generate_mock_chapter(self, story_data: Dict[str, Any], previous_choice: str = None) -> Dict[str, Any]:
        """生成模拟章节内容（用于测试）"""
        chapter_num = story_data.get('current_chapter_number', 1)
        style = story_data.get('style', '修仙')
        
        mock_content = {
            '修仙': f"第{chapter_num}章：修炼之路\n\n在这个充满灵气的修仙世界中，主角踏上了修炼的道路。经过刻苦的修炼，实力不断提升。面对前方的挑战，需要做出重要的选择...",
            '武侠': f"第{chapter_num}章：江湖风云\n\n江湖之中，风云变幻。主角凭借着一身武艺，在江湖中闯荡。面对强敌的挑战，需要运用智慧和武功来应对...",
            '科技': f"第{chapter_num}章：星际探索\n\n在遥远的未来，人类已经掌握了星际航行技术。主角作为一名探索者，在宇宙中寻找新的文明。面对未知的挑战，科技将是最好的武器..."
        }
        
        return {
            "title": f"第{chapter_num}章",
            "content": mock_content.get(style, mock_content['修仙'])
        }
    
    def _generate_mock_choices(self, style: StoryStyle) -> List[str]:
        """生成模拟选择（用于测试）"""
        mock_choices = {
            StoryStyle.XIANXIA: [
                "选择加入强大的门派，获得更好的修炼资源",
                "选择独自修炼，走出属于自己的道路",
                "选择寻找传说中的秘境，寻求机缘"
            ],
            StoryStyle.WUXIA: [
                "选择行侠仗义，帮助弱小",
                "选择专心练武，提升武功",
                "选择调查江湖传言，寻找真相"
            ],
            StoryStyle.SCIFI: [
                "选择升级飞船系统，提高探索能力",
                "选择与外星文明建立联系",
                "选择深入未知星域，寻找新发现"
            ]
        }
        return mock_choices.get(style, mock_choices[StoryStyle.XIANXIA])

# 创建全局AI服务实例
ai_service = AIService()