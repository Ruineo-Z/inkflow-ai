# AI交互式小说后端API

基于FastAPI的AI交互式小说后端服务，集成Google Gemini AI模型，支持三种风格的小说生成（修仙、武侠、科技）。

## 功能特性

- 🤖 **AI驱动**: 集成Google Gemini AI模型进行内容生成
- 📚 **多风格支持**: 修仙、武侠、科技三种小说风格
- 🎯 **交互式选择**: 用户选择驱动故事发展
- 🗄️ **数据持久化**: PostgreSQL数据库存储
- 🚀 **高性能**: FastAPI异步框架
- 🔧 **易于扩展**: 模块化架构设计

## 技术栈

- **后端框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy ORM
- **AI模型**: Google Gemini API
- **Python版本**: 3.8+

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/              # 数据模型
│   │   ├── story.py
│   │   ├── chapter.py
│   │   └── choice.py
│   ├── api/                 # API路由
│   │   ├── stories.py
│   │   └── chapters.py
│   ├── services/            # 业务逻辑
│   │   ├── ai_service.py
│   │   └── story_service.py
│   ├── database/            # 数据库配置
│   │   └── connection.py
│   └── config/              # 配置文件
│       └── settings.py
├── tests/                   # 测试文件
├── requirements.txt         # 项目依赖
├── .env.example            # 环境变量模板
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置以下关键参数：
# - DATABASE_URL: PostgreSQL数据库连接字符串
# - GEMINI_API_KEY: Google Gemini API密钥
```

### 3. 数据库设置

```bash
# 确保PostgreSQL服务运行
# 创建数据库
createdb ai_novel_db
```

### 4. 启动服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python -m app.main
```

服务启动后，访问 http://localhost:8000 查看API文档。

## API接口

### 故事管理

- `POST /api/stories` - 创建新故事
- `GET /api/stories/{id}` - 获取故事详情
- `GET /api/stories/{id}/chapters` - 获取故事章节列表
- `POST /api/stories/{id}/chapters` - 生成新章节
- `GET /api/stories/{id}/choices` - 获取选择历史

### 章节管理

- `GET /api/chapters/{id}` - 获取章节详情
- `POST /api/chapters/{id}/choices` - 提交选择并生成下一章
- `GET /api/chapters/{id}/choices` - 获取章节选择选项

### 使用示例

```python
import requests

# 创建故事
response = requests.post('http://localhost:8000/api/stories', json={
    'style': '修仙',
    'title': '修仙传奇'
})
story = response.json()['data']

# 生成第一章
response = requests.post(f'http://localhost:8000/api/stories/{story["id"]}/chapters')
chapter = response.json()['data']

# 提交选择
response = requests.post(f'http://localhost:8000/api/chapters/{chapter["id"]}/choices', json={
    'choice_id': chapter['choices'][0]['id']
})
next_chapter = response.json()['data']
```

## 开发指南

### 添加新的故事风格

1. 在 `app/models/story.py` 中添加新的 `StoryStyle` 枚举值
2. 在 `app/services/ai_service.py` 中添加对应的prompt模板
3. 更新相关的测试用例

### 自定义AI提示词

编辑 `app/services/ai_service.py` 中的 `_get_style_prompt` 方法，调整不同风格的prompt模板。

### 数据库迁移

```bash
# 安装Alembic（如果需要）
pip install alembic

# 初始化迁移
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_stories.py

# 生成测试覆盖率报告
pytest --cov=app
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ai-novel-api .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-novel-api
```

### 生产环境

```bash
# 使用Gunicorn启动
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目链接: [https://github.com/your-username/ai-novel-backend](https://github.com/your-username/ai-novel-backend)
- 问题反馈: [Issues](https://github.com/your-username/ai-novel-backend/issues)