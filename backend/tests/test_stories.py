import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import StoryStyle

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestStories:
    def test_create_story(self):
        """测试创建故事"""
        response = client.post("/api/stories/", json={
            "style": "修仙",
            "title": "测试修仙故事"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["style"] == "修仙"
        assert data["data"]["title"] == "测试修仙故事"
        assert data["data"]["status"] == "active"
    
    def test_create_story_without_title(self):
        """测试创建故事（不指定标题）"""
        response = client.post("/api/stories/", json={
            "style": "武侠"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["style"] == "武侠"
        assert "title" in data["data"]
    
    def test_get_story(self):
        """测试获取故事详情"""
        # 先创建一个故事
        create_response = client.post("/api/stories/", json={
            "style": "科技",
            "title": "科幻冒险"
        })
        story_id = create_response.json()["data"]["id"]
        
        # 获取故事详情
        response = client.get(f"/api/stories/{story_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == story_id
        assert data["data"]["style"] == "科技"
    
    def test_get_nonexistent_story(self):
        """测试获取不存在的故事"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/stories/{fake_id}")
        
        assert response.status_code == 404
    
    def test_generate_first_chapter(self):
        """测试生成第一章"""
        # 创建故事
        create_response = client.post("/api/stories/", json={
            "style": "修仙",
            "title": "修仙之路"
        })
        story_id = create_response.json()["data"]["id"]
        
        # 生成第一章
        response = client.post(f"/api/stories/{story_id}/chapters")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "chapter_id" in data["data"]
        assert "title" in data["data"]
        assert "content" in data["data"]
        assert "choices" in data["data"]
        assert len(data["data"]["choices"]) == 3
    
    def test_get_story_chapters(self):
        """测试获取故事章节列表"""
        # 创建故事并生成第一章
        create_response = client.post("/api/stories/", json={
            "style": "武侠"
        })
        story_id = create_response.json()["data"]["id"]
        
        client.post(f"/api/stories/{story_id}/chapters")
        
        # 获取章节列表
        response = client.get(f"/api/stories/{story_id}/chapters")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["chapters"]) == 1
    
    def test_get_story_choices_history(self):
        """测试获取选择历史"""
        # 创建故事
        create_response = client.post("/api/stories/", json={
            "style": "科技"
        })
        story_id = create_response.json()["data"]["id"]
        
        # 获取选择历史（应该为空）
        response = client.get(f"/api/stories/{story_id}/choices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["choices_history"] == []

class TestChapters:
    def test_get_chapter(self):
        """测试获取章节详情"""
        # 创建故事并生成第一章
        create_response = client.post("/api/stories/", json={
            "style": "修仙"
        })
        story_id = create_response.json()["data"]["id"]
        
        chapter_response = client.post(f"/api/stories/{story_id}/chapters")
        chapter_id = chapter_response.json()["data"]["id"]
        
        # 获取章节详情
        response = client.get(f"/api/chapters/{chapter_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == chapter_id
    
    def test_get_chapter_choices(self):
        """测试获取章节选择选项"""
        # 创建故事并生成第一章
        create_response = client.post("/api/stories/", json={
            "style": "武侠"
        })
        story_id = create_response.json()["data"]["id"]
        
        chapter_response = client.post(f"/api/stories/{story_id}/chapters")
        chapter_id = chapter_response.json()["data"]["id"]
        
        # 获取选择选项
        response = client.get(f"/api/chapters/{chapter_id}/choices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["choices"]) == 3
    
    def test_submit_ai_choice(self):
        """测试提交AI生成的选择"""
        # 创建故事并生成第一章
        create_response = client.post("/api/stories/", json={
            "style": "科技"
        })
        story_id = create_response.json()["data"]["id"]
        
        chapter_response = client.post(f"/api/stories/{story_id}/chapters")
        chapter_data = chapter_response.json()["data"]
        chapter_id = chapter_data["id"]
        choice_id = chapter_data["choices"][0]["id"]
        
        # 提交选择
        response = client.post(f"/api/chapters/{chapter_id}/choices", json={
            "choice_id": choice_id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["chapter_number"] == 2
    
    def test_submit_custom_choice(self):
        """测试提交自定义选择"""
        # 创建故事并生成第一章
        create_response = client.post("/api/stories/", json={
            "style": "修仙"
        })
        story_id = create_response.json()["data"]["id"]
        
        chapter_response = client.post(f"/api/stories/{story_id}/chapters")
        chapter_id = chapter_response.json()["data"]["id"]
        
        # 提交自定义选择
        response = client.post(f"/api/chapters/{chapter_id}/choices", json={
            "custom_choice": "我选择寻找传说中的仙人洞府"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["chapter_number"] == 2

class TestHealthCheck:
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data