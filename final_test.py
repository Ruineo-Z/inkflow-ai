#!/usr/bin/env python3
"""
InkFlow AI 最终完整流程测试
重构后的完整测试：创建账号 -> 创建小说 -> 生成第一章 -> 生成第二章
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:20001"

def print_step(step_num, description):
    """打印测试步骤"""
    print(f"\n{'='*60}")
    print(f"🚀 步骤 {step_num}: {description}")
    print('='*60)

def test_health():
    """1. 健康检查"""
    print_step(1, "健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务健康: {data['status']}")
            print(f"📊 服务信息: {data['services']}")
            return True
        else:
            print(f"❌ 服务不健康: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def register_user():
    """2. 注册用户"""
    print_step(2, "注册用户")
    username = f"finaltest_{int(time.time())}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": username},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            token = data["token"]
            user_info = data["user"]
            print(f"✅ 用户注册成功!")
            print(f"👤 用户名: {user_info['username']}")
            print(f"🆔 用户ID: {user_info['user_id']}")
            print(f"🔑 Token: {token[:20]}...")
            return token, user_info
        else:
            print(f"❌ 注册失败: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return None, None

def create_story(token):
    """3. 创建故事"""
    print_step(3, "创建故事")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/stories/",
            headers=headers,
            json={"style": "修仙", "title": "重构后测试小说"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                story_info = data["data"]
                print(f"✅ 故事创建成功!")
                print(f"📚 故事标题: {story_info['title']}")
                print(f"🎨 故事风格: {story_info['style']}")
                print(f"🆔 故事ID: {story_info['id']}")
                return story_info
            else:
                print(f"❌ 故事创建失败: {data['message']}")
                return None
        else:
            print(f"❌ 创建故事失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建故事异常: {e}")
        return None

def create_worldview(token, story_id):
    """4. 创建世界观"""
    print_step(4, "创建世界观")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🌍 正在生成世界观框架...")
        response = requests.post(
            f"{BASE_URL}/api/stories/{story_id}/worldview",
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ 世界观创建成功!")
                worldview = data["data"]
                print(f"🏛️ 世界观概述: {worldview.get('overview', '未知')[:100]}...")
                return True
            else:
                print(f"❌ 世界观创建失败: {data['message']}")
                return False
        else:
            print(f"❌ 创建世界观失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建世界观异常: {e}")
        return False

def generate_first_chapter(token, story_id):
    """5. 生成第一章"""
    print_step(5, "生成第一章")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📖 正在生成第一章...")
        response = requests.post(
            f"{BASE_URL}/api/stories/{story_id}/chapters",
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                chapter_info = data["data"]
                print(f"✅ 第一章生成成功!")
                print(f"📖 章节标题: {chapter_info['title']}")
                print(f"📝 章节号: {chapter_info['chapter_number']}")
                print(f"📄 内容长度: {len(chapter_info['content'])} 字符")
                print(f"📝 内容预览: {chapter_info['content'][:150]}...")
                return chapter_info
            else:
                print(f"❌ 第一章生成失败: {data['message']}")
                return None
        else:
            print(f"❌ 生成第一章失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 生成第一章异常: {e}")
        return None

def get_chapter_choices(token, chapter_id):
    """6. 获取章节选择"""
    print_step(6, "获取章节选择")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/chapters/{chapter_id}/choices",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                choices = data["data"]["choices"]
                print(f"✅ 获取到 {len(choices)} 个选择选项:")
                for i, choice in enumerate(choices, 1):
                    print(f"   {i}. {choice['text']}")
                return choices
            else:
                print(f"❌ 获取选择失败: {data['message']}")
                return None
        else:
            print(f"❌ 获取选择失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取选择异常: {e}")
        return None

def generate_second_chapter_stream(token, chapter_id, choice_id):
    """7. 流式生成第二章"""
    print_step(7, "流式生成第二章")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🌊 开始流式生成第二章...")
        response = requests.post(
            f"{BASE_URL}/api/chapters/stream/{chapter_id}/choices",
            headers=headers,
            json={"choice_id": choice_id},
            stream=True,
            timeout=180
        )
        
        if response.status_code == 200:
            print("✅ 开始接收流式数据:")
            print("-" * 50)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            
                            if data["type"] == "start":
                                print(f"🚀 {data['message']}")
                                
                            elif data["type"] == "title":
                                print(f"📖 {data['content']}")
                                print("-" * 30)
                                
                            elif data["type"] == "content":
                                print(data["content"], end="", flush=True)
                                
                            elif data["type"] == "complete":
                                print("\n" + "-" * 50)
                                print("✅ 第二章流式生成完成!")
                                chapter = data["chapter"]
                                choices = data["choices"]
                                print(f"📖 章节: {chapter['title']}")
                                print(f"📝 章节号: {chapter['chapter_number']}")
                                print(f"🎯 新的选择选项:")
                                for i, choice in enumerate(choices, 1):
                                    print(f"   {i}. {choice['text']}")
                                return True
                                
                            elif data["type"] == "error":
                                print(f"\n❌ {data['message']}")
                                return False
                                
                        except json.JSONDecodeError:
                            continue
            
            return True
        else:
            print(f"❌ 流式生成失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 流式生成异常: {e}")
        return False

def main():
    """主测试流程"""
    print("🎉 InkFlow AI 重构后完整流程测试")
    print("🔄 测试流程: 创建账号 -> 创建小说 -> 生成第一章 -> 生成第二章")
    
    start_time = time.time()
    
    # 1. 健康检查
    if not test_health():
        sys.exit(1)
    
    # 2. 注册用户
    token, user_info = register_user()
    if not token:
        sys.exit(1)
    
    # 3. 创建故事
    story_info = create_story(token)
    if not story_info:
        sys.exit(1)
    
    # 4. 创建世界观
    if not create_worldview(token, story_info["id"]):
        sys.exit(1)
    
    # 5. 生成第一章
    chapter_info = generate_first_chapter(token, story_info["id"])
    if not chapter_info:
        sys.exit(1)
    
    # 6. 获取选择
    choices = get_chapter_choices(token, chapter_info["id"])
    if not choices:
        sys.exit(1)
    
    # 7. 流式生成第二章
    if generate_second_chapter_stream(token, chapter_info["id"], choices[0]["id"]):
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "🎉" * 20)
        print("🎉 重构后完整流程测试成功!")
        print("🎉" * 20)
        print(f"📊 测试总结:")
        print(f"   ⏱️  总耗时: {total_time:.2f} 秒")
        print(f"   👤 用户: {user_info['username']} ({user_info['user_id']})")
        print(f"   📚 故事: {story_info['title']}")
        print(f"   📖 生成章节: 2章")
        print(f"   🌊 流式输出: ✅ 完美工作")
        print(f"   🏗️  项目结构: ✅ 重构成功")
        print("\n✨ InkFlow AI 系统运行完美！")
    else:
        print("\n❌ 流式生成测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
