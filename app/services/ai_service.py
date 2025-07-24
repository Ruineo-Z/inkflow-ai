import google.generativeai as genai
from typing import List, Dict, Any, AsyncGenerator
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
    
    def _build_context(self, story_data: Dict[str, Any], worldview_context: str = None, previous_choice: str = None) -> str:
        """构建故事上下文"""
        context = f"故事风格：{story_data.get('style', '')}\n"
        context += f"故事标题：{story_data.get('title', '')}\n"
        
        # 添加世界观框架
        if worldview_context:
            context += f"\n世界观框架：\n{worldview_context}\n"
        
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
    
    async def generate_worldview(self, story_title: str, story_style: StoryStyle, story_theme: str = None) -> Dict[str, Any]:
        """生成世界观框架"""
        print(f"生成世界观 - 标题: {story_title}, 风格: {story_style.value}")
        
        # 检查Gemini API配置
        if not self.model:
            raise Exception("Gemini API未配置或配置错误，无法生成世界观")
        
        try:
            # 根据风格构建世界观生成提示词
            style_specific_prompts = {
                StoryStyle.XIANXIA: """
请为修仙小说创建详细的世界观框架，包含：
- 修炼体系：境界划分、修炼方法、灵气设定
- 门派势力：各大门派、势力分布、关系网络
- 地理环境：修仙界地图、秘境、险地
- 历史背景：上古传说、重大事件、时代变迁
- 主角设定：出身背景、天赋特点、初始实力
- 主线剧情：成长路线、主要冲突、终极目标
""",
                StoryStyle.WUXIA: """
请为武侠小说创建详细的世界观框架，包含：
- 武功体系：内功外功、武学流派、绝世神功
- 江湖势力：门派帮会、朝廷势力、江湖规矩
- 地理环境：江湖地图、名山大川、隐秘之地
- 历史背景：武林历史、恩怨情仇、传奇人物
- 主角设定：出身来历、武学天赋、性格特点
- 主线剧情：江湖路线、主要矛盾、最终目标
""",
                StoryStyle.SCIFI: """
请为科幻小说创建详细的世界观框架，包含：
- 科技体系：未来科技、AI系统、星际文明
- 社会结构：政治体制、经济模式、阶层分化
- 地理环境：星际地图、殖民星球、太空站点
- 历史背景：科技发展史、重大事件、文明冲突
- 主角设定：职业背景、技能特长、使命目标
- 主线剧情：探索路线、核心冲突、终极愿景
"""
            }
            
            base_prompt = style_specific_prompts.get(story_style, style_specific_prompts[StoryStyle.XIANXIA])
            
            theme_context = f"\n故事主题：{story_theme}" if story_theme else ""
            
            prompt = f"""
你是一位专业的{story_style.value}小说世界观设计师。请为小说《{story_title}》创建完整的世界观框架。

{base_prompt}
{theme_context}

请返回JSON格式的世界观框架，包含以下字段：
{{
    "world_setting": "世界设定的总体描述",
    "power_system": "力量体系的详细说明",
    "social_structure": "社会结构和势力分布",
    "geography": "地理环境和重要地点",
    "history_background": "历史背景和重要事件",
    "main_character": {{
        "name": "主角姓名",
        "description": "主角详细设定",
        "background": "出身背景",
        "abilities": "初始能力",
        "goals": "主要目标"
    }},
    "main_plot": "主线剧情框架",
    "conflict_setup": "主要冲突设置",
    "story_themes": ["主题1", "主题2", "主题3"],
    "narrative_style": "叙述风格特点",
    "tone_atmosphere": "整体基调和氛围"
}}
"""
            
            response = await self.model.generate_content_async(prompt)
            
            # 解析AI响应
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                else:
                    content = ""
            else:
                content = ""
            
            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*"world_setting"[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 如果无法解析JSON，返回默认结构
            return {
                "world_setting": f"这是一个{story_style.value}风格的世界，充满了神秘和冒险。",
                "power_system": "待完善的力量体系",
                "social_structure": "复杂的社会结构",
                "geography": "广阔的世界地图",
                "history_background": "悠久的历史传承",
                "main_character": {
                    "name": "主角",
                    "description": "一位有着特殊命运的年轻人",
                    "background": "普通出身",
                    "abilities": "潜力无限",
                    "goals": "成为最强者"
                },
                "main_plot": "主角的成长和冒险之路",
                "conflict_setup": "正义与邪恶的较量",
                "story_themes": ["成长", "友情", "正义"],
                "narrative_style": "生动有趣的叙述",
                "tone_atmosphere": "积极向上的氛围"
            }
            
        except Exception as e:
            print(f"AI生成世界观失败: {e}")
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
    async def generate_chapter(self, story_data: Dict[str, Any], worldview_context: str = None, previous_choice: str = None) -> Dict[str, Any]:
        """生成章节内容"""
        print(f"生成章节 - 故事ID: {story_data.get('title', 'Unknown')}, 章节: {story_data.get('current_chapter_number', 1)}")
        
        # 检查Gemini API配置
        if not self.model:
            raise Exception("Gemini API未配置或配置错误，无法生成内容")
        
        try:
            style = StoryStyle(story_data['style'])
            style_prompt = self._get_style_prompt(style)
            context = self._build_context(story_data, worldview_context, previous_choice)
            
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
            
            # 解析AI响应 - 使用正确的访问方式
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                else:
                    content = ""
            else:
                content = ""
            
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
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
    async def generate_chapter_stream(self, story_data: Dict[str, Any], worldview_context: str = None, previous_choice: str = None):
        """流式生成章节内容"""
        print(f"流式生成章节 - 故事ID: {story_data.get('title', 'Unknown')}, 章节: {story_data.get('current_chapter_number', 1)}")
        
        # 检查Gemini API配置
        if not self.model:
            raise Exception("Gemini API未配置或配置错误，无法生成内容")
        
        try:
            style = StoryStyle(story_data['style'])
            style_prompt = self._get_style_prompt(style)
            context = self._build_context(story_data, worldview_context, previous_choice)
            
            prompt = f"""{style_prompt}

{context}

请基于以上信息，创作下一章节的内容。要求：
1. 章节内容要连贯自然，与之前的情节呼应
2. 如果有用户选择，要体现选择的影响
3. 在章节结尾设置适当的悬念
4. 直接输出章节内容，不需要JSON格式
5. 章节标题单独一行，然后是章节内容"""
            
            # 使用流式生成
            response = self.model.generate_content(prompt, stream=True)
            
            accumulated_content = ""
            title = f"第{story_data.get('current_chapter_number', 1)}章"
            title_sent = False
            
            for chunk in response:
                if chunk.candidates and len(chunk.candidates) > 0:
                    candidate = chunk.candidates[0]
                    if candidate.content and candidate.content.parts:
                        chunk_text = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                        accumulated_content += chunk_text
                        
                        # 首次发送标题
                        if not title_sent:
                            yield {
                                "type": "title",
                                "content": title
                            }
                            title_sent = True
                        
                        # 发送内容块
                        yield {
                            "type": "content",
                            "content": chunk_text
                        }
            
            # 发送完成信号
            yield {
                "type": "complete",
                "title": title,
                "content": accumulated_content.strip()
            }
            
        except Exception as e:
            print(f"AI流式生成章节失败: {e}")
            yield {
                "type": "error",
                "message": f"Gemini API调用失败: {str(e)}"
            }
    
    async def generate_choices(self, chapter_content: str, story_style: StoryStyle) -> List[str]:
        """生成选择选项"""
        print(f"生成选择 - 风格: {story_style.value}")
        
        # 检查Gemini API配置
        if not self.model:
            raise Exception("Gemini API未配置或配置错误，无法生成选择")
        
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
            
            # 解析AI响应 - 使用正确的访问方式
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    content = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                else:
                    content = ""
            else:
                content = ""
            
            # 尝试解析JSON数组
            json_match = re.search(r'\[[^\[\]]*\]', content)
            if json_match:
                try:
                    choices = json.loads(json_match.group())
                    if isinstance(choices, list) and len(choices) >= 3:
                        return choices[:3]
                except json.JSONDecodeError:
                    pass
            
            # 如果解析失败，抛出错误
            raise Exception("Gemini API返回格式解析失败")
            
        except Exception as e:
            print(f"AI生成选择失败: {e}")
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
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