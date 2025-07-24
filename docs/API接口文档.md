# InkFlow AI - API接口文档

## 概述

InkFlow AI 是一个基于 FastAPI 的 AI 交互式小说后端服务，提供用户认证、故事管理、章节生成和选择交互等功能。

**基础信息：**
- 基础URL: `http://localhost:20001`
- API前缀: `/api`
- 认证方式: Bearer Token (JWT)
- 内容类型: `application/json`

## 认证说明

除了公共接口外，所有API都需要在请求头中携带有效的JWT token：

```http
Authorization: Bearer <your_jwt_token>
```

## 公共接口

### 1. 根路径

**GET** `/`

获取API基本信息。

**响应示例：**
```json
{
  "message": "AI Interactive Novel API",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. 健康检查

**GET** `/health`

检查服务健康状态。

**响应示例：**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

## 用户认证 API

### 1. 用户注册

**POST** `/api/auth/register`

创建新用户账户。

**请求体：**
```json
{
  "username": "string"
}
```

**响应示例：**
```json
{
  "message": "用户注册成功",
  "user": {
    "username": "testuser",
    "user_id": "ABC123DEF456",
    "created_at": "2024-01-01T00:00:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. 用户登录

**POST** `/api/auth/login`

使用用户ID登录获取token。

**请求体：**
```json
{
  "user_id": "ABC123DEF456"
}
```

**响应示例：**
```json
{
  "message": "登录成功",
  "user": {
    "username": "testuser",
    "user_id": "ABC123DEF456",
    "created_at": "2024-01-01T00:00:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前认证用户的信息。

**响应示例：**
```json
{
  "username": "testuser",
  "user_id": "ABC123DEF456",
  "created_at": "2024-01-01T00:00:00"
}
```

### 4. 验证Token

**POST** `/api/auth/verify`

验证JWT token的有效性。

**响应示例：**
```json
{
  "valid": true,
  "user": {
    "id": "user-uuid",
    "username": "testuser"
  },
  "error": null
}
```

## 故事管理 API

### 1. 获取用户所有故事

**GET** `/api/stories/`

获取当前用户的所有故事列表。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "stories": [
      {
        "id": "story-uuid",
        "title": "修仙传奇",
        "style": "修仙",
        "status": "active",
        "current_chapter_number": 3,
        "user_id": "user-uuid",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "state_data": {},
        "chapter_summaries": [],
        "character_info": {}
      }
    ]
  },
  "message": ""
}
```

### 2. 创建新故事

**POST** `/api/stories/`

创建一个新的故事。

**请求体：**
```json
{
  "style": "修仙",  // 可选值: "修仙", "武侠", "科技"
  "title": "我的修仙之路"  // 可选，不提供则自动生成
}
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "story": {
      "id": "story-uuid",
      "title": "我的修仙之路",
      "style": "修仙",
      "status": "active",
      "current_chapter_number": 0,
      "user_id": "user-uuid",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "state_data": {},
      "chapter_summaries": [],
      "character_info": {}
    }
  },
  "message": "故事创建成功"
}
```

### 3. 获取故事详情

**GET** `/api/stories/{story_id}`

获取指定故事的详细信息。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "story": {
      "id": "story-uuid",
      "title": "修仙传奇",
      "style": "修仙",
      "status": "active",
      "current_chapter_number": 3,
      "user_id": "user-uuid",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00",
      "state_data": {},
      "chapter_summaries": [],
      "character_info": {}
    }
  },
  "message": ""
}
```

### 4. 获取故事章节列表

**GET** `/api/stories/{story_id}/chapters`

获取指定故事的所有章节。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "chapters": [
      {
        "id": "chapter-uuid",
        "story_id": "story-uuid",
        "chapter_number": 1,
        "title": "初入修仙界",
        "content": "章节内容...",
        "summary": "章节摘要",
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "message": ""
}
```

### 5. 生成新章节

**POST** `/api/stories/{story_id}/chapters`

为指定故事生成新的章节。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "chapter": {
      "id": "chapter-uuid",
      "story_id": "story-uuid",
      "chapter_number": 2,
      "title": "遇见师父",
      "content": "新章节内容...",
      "summary": "章节摘要",
      "created_at": "2024-01-01T00:00:00"
    },
    "choices": [
      {
        "id": "choice-uuid",
        "chapter_id": "chapter-uuid",
        "text": "选择拜师学艺",
        "choice_type": "ai_generated",
        "is_selected": false,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "message": "章节生成成功"
}
```

### 6. 获取故事选择历史

**GET** `/api/stories/{story_id}/choices`

获取故事中所有已选择的选项历史。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "choices_history": [
      {
        "chapter_number": 1,
        "chapter_title": "初入修仙界",
        "selected_choice": "选择进入宗门",
        "choice_type": "ai_generated",
        "selected_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "message": ""
}
```

### 7. 删除故事

**DELETE** `/api/stories/{story_id}`

删除指定的故事及其所有章节。

**响应示例：**
```json
{
  "success": true,
  "data": {},
  "message": "故事删除成功"
}
```

## 章节管理 API

### 1. 获取章节详情

**GET** `/api/chapters/{chapter_id}`

获取指定章节的详细信息。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "chapter": {
      "id": "chapter-uuid",
      "story_id": "story-uuid",
      "chapter_number": 1,
      "title": "初入修仙界",
      "content": "章节内容...",
      "summary": "章节摘要",
      "created_at": "2024-01-01T00:00:00"
    }
  },
  "message": ""
}
```

### 2. 提交选择并生成下一章节

**POST** `/api/chapters/{chapter_id}/choices`

提交用户选择并生成下一个章节。

**请求体：**
```json
{
  "choice_id": "choice-uuid",     // AI生成的选择ID
  "custom_choice": "自定义选择"    // 用户自定义选择文本
}
```

**注意：** `choice_id` 和 `custom_choice` 二选一，不能同时提供。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "next_chapter": {
      "id": "next-chapter-uuid",
      "story_id": "story-uuid",
      "chapter_number": 2,
      "title": "遇见师父",
      "content": "新章节内容...",
      "summary": "章节摘要",
      "created_at": "2024-01-01T00:00:00"
    },
    "choices": [
      {
        "id": "choice-uuid",
        "chapter_id": "next-chapter-uuid",
        "text": "选择拜师学艺",
        "choice_type": "ai_generated",
        "is_selected": false,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "message": "下一章节生成成功"
}
```

### 3. 获取章节选择选项

**GET** `/api/chapters/{chapter_id}/choices`

获取指定章节的所有选择选项。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "choices": [
      {
        "id": "choice-uuid",
        "chapter_id": "chapter-uuid",
        "text": "选择进入宗门",
        "choice_type": "ai_generated",
        "is_selected": false,
        "created_at": "2024-01-01T00:00:00"
      }
    ]
  },
  "message": ""
}
```

### 4. 流式生成下一章节

**POST** `/api/chapters/stream/{chapter_id}/choices`

提交选择并以流式方式生成下一章节（实时返回生成内容）。

**请求体：**
```json
{
  "choice_id": "choice-uuid",
  "custom_choice": "自定义选择"
}
```

**响应：** Server-Sent Events (SSE) 流

```
data: {"type": "chapter_start", "data": {"chapter_number": 2}}

data: {"type": "content_chunk", "data": {"text": "章节内容片段..."}}

data: {"type": "chapter_complete", "data": {"chapter": {...}, "choices": [...]}}
```

## 数据模型

### User (用户)
```json
{
  "id": "string (UUID)",
  "username": "string",
  "user_id": "string (12位随机ID)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Story (故事)
```json
{
  "id": "string (UUID)",
  "title": "string",
  "style": "enum (修仙|武侠|科技)",
  "status": "enum (active|completed|paused)",
  "current_chapter_number": "integer",
  "user_id": "string (UUID)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "state_data": "object",
  "chapter_summaries": "array",
  "character_info": "object"
}
```

### Chapter (章节)
```json
{
  "id": "string (UUID)",
  "story_id": "string (UUID)",
  "chapter_number": "integer",
  "title": "string",
  "content": "string",
  "summary": "string",
  "created_at": "datetime"
}
```

### Choice (选择)
```json
{
  "id": "string (UUID)",
  "chapter_id": "string (UUID)",
  "text": "string",
  "choice_type": "enum (ai_generated|user_custom)",
  "is_selected": "boolean",
  "created_at": "datetime"
}
```

## 错误响应

### 认证错误 (401)
```json
{
  "detail": "Invalid or expired token"
}
```

### 权限错误 (403)
```json
{
  "detail": "Not enough permissions"
}
```

### 资源不存在 (404)
```json
{
  "detail": "Resource not found"
}
```

### 验证错误 (422)
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 服务器错误 (500)
```json
{
  "success": false,
  "data": {},
  "message": "内部服务器错误"
}
```

## 使用示例

### 完整的用户流程

1. **用户注册**
```bash
curl -X POST "http://localhost:20001/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

2. **用户登录**
```bash
curl -X POST "http://localhost:20001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "ABC123DEF456"}'
```

3. **创建故事**
```bash
curl -X POST "http://localhost:20001/api/stories/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"style": "修仙", "title": "我的修仙之路"}'
```

4. **生成首章**
```bash
curl -X POST "http://localhost:20001/api/stories/{story_id}/chapters" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

5. **提交选择生成下一章**
```bash
curl -X POST "http://localhost:20001/api/chapters/{chapter_id}/choices" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"choice_id": "choice-uuid"}'
```

## 开发工具

- **API文档**: `http://localhost:20001/docs` (Swagger UI)
- **OpenAPI规范**: `http://localhost:20001/openapi.json`
- **ReDoc文档**: `http://localhost:20001/redoc`

## 注意事项

1. 所有需要认证的接口都必须在请求头中携带有效的JWT token
2. Token有效期为30分钟，过期后需要重新登录
3. 用户只能访问自己创建的故事和章节
4. 故事风格目前支持：修仙、武侠、科技
5. 章节生成使用Google Gemini AI模型
6. 支持用户自定义选择和AI生成选择两种模式
7. 流式接口适用于需要实时显示生成过程的场景