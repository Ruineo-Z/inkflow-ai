# AI交互式小说 API接口文档

基于FastAPI自动生成的OpenAPI规范，以下是完整的API接口文档：

## 基本信息
- **API标题**: AI Interactive Novel API
- **版本**: 1.0.0
- **基础URL**: http://localhost:8000

## API端点

### 1. 故事管理

#### 创建新故事
- **端点**: `POST /api/stories/`
- **描述**: 创建新故事
- **请求体**:
  ```json
  {
    "style": "修仙" | "武侠" | "科技",
    "title": "string" (可选)
  }
  ```
- **响应**: StoryResponse

#### 获取故事详情
- **端点**: `GET /api/stories/{story_id}`
- **描述**: 获取故事详情
- **路径参数**: 
  - `story_id` (string, 必需)
- **响应**: StoryResponse

#### 获取故事章节列表
- **端点**: `GET /api/stories/{story_id}/chapters`
- **描述**: 获取故事章节列表
- **路径参数**: 
  - `story_id` (string, 必需)
- **响应**: 章节列表

#### 生成新章节
- **端点**: `POST /api/stories/{story_id}/chapters`
- **描述**: 生成新章节
- **路径参数**: 
  - `story_id` (string, 必需)
- **响应**: ChapterResponse

#### 获取故事选择历史
- **端点**: `GET /api/stories/{story_id}/choices`
- **描述**: 获取故事选择历史
- **路径参数**: 
  - `story_id` (string, 必需)
- **响应**: 选择历史列表

### 2. 章节管理

#### 获取章节详情
- **端点**: `GET /api/chapters/{chapter_id}`
- **描述**: 获取章节详情
- **路径参数**: 
  - `chapter_id` (string, 必需)
- **响应**: ChapterResponse

#### 获取章节选择选项
- **端点**: `GET /api/chapters/{chapter_id}/choices`
- **描述**: 获取章节的选择选项
- **路径参数**: 
  - `chapter_id` (string, 必需)
- **响应**: 选择选项列表

#### 提交用户选择
- **端点**: `POST /api/chapters/{chapter_id}/choices`
- **描述**: 提交用户选择并生成下一章
- **路径参数**: 
  - `chapter_id` (string, 必需)
- **请求体**:
  ```json
  {
    "choice_id": "string" | null,
    "custom_choice": "string" | null
  }
  ```
- **响应**: NextChapterResponse

### 3. 系统端点

#### 根路径
- **端点**: `GET /`
- **描述**: 根路径
- **响应**: 基本信息

#### 健康检查
- **端点**: `GET /health`
- **描述**: 健康检查
- **响应**: 健康状态

## 数据模型

### StoryStyle (枚举)
```
"修仙" | "武侠" | "科技"
```

### CreateStoryRequest
```json
{
  "style": "StoryStyle",
  "title": "string" (可选)
}
```

### StoryResponse
```json
{
  "success": boolean,
  "data": object,
  "message": "string" (默认: "")
}
```

### ChapterResponse
```json
{
  "success": boolean,
  "data": object,
  "message": "string" (默认: "")
}
```

### NextChapterResponse
```json
{
  "success": boolean,
  "data": object,
  "message": "string" (默认: "")
}
```

### SubmitChoiceRequest
```json
{
  "choice_id": "string" | null,
  "custom_choice": "string" | null
}
```

### HTTPValidationError
```json
{
  "detail": [
    {
      "loc": ["string" | integer],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## 使用示例

### 创建新故事
```bash
curl -X POST "http://localhost:8000/api/stories/" \
  -H "Content-Type: application/json" \
  -d '{"style": "修仙", "title": "我的修仙之路"}'
```

### 获取故事详情
```bash
curl "http://localhost:8000/api/stories/{story_id}"
```

### 生成新章节
```bash
curl -X POST "http://localhost:8000/api/stories/{story_id}/chapters"
```

### 提交选择
```bash
curl -X POST "http://localhost:8000/api/chapters/{chapter_id}/choices" \
  -H "Content-Type: application/json" \
  -d '{"choice_id": "choice_1"}'
```

## 错误处理

所有API端点都可能返回以下HTTP状态码：
- **200**: 成功
- **422**: 验证错误 (返回HTTPValidationError)
- **500**: 服务器内部错误

## 注意事项

1. 所有响应都遵循统一的格式：`{"success": boolean, "data": object, "message": string}`
2. 故事风格必须是预定义的枚举值之一："修仙"、"武侠"、"科技"
3. 用户可以通过choice_id选择预设选项，或通过custom_choice提交自定义选择
4. API支持中文内容，请确保使用UTF-8编码