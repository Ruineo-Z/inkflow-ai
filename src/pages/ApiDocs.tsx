import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Book, Code, Copy, ExternalLink, CheckCircle } from 'lucide-react'

export default function ApiDocs() {
  const navigate = useNavigate()
  const [copiedEndpoint, setCopiedEndpoint] = useState<string | null>(null)

  const copyToClipboard = (text: string, endpoint: string) => {
    navigator.clipboard.writeText(text)
    setCopiedEndpoint(endpoint)
    setTimeout(() => setCopiedEndpoint(null), 2000)
  }

  const endpoints = [
    {
      method: 'POST',
      path: '/api/stories/',
      description: '创建新故事',
      requestBody: `{
  "style": "修仙" | "武侠" | "科技",
  "title": "string" (可选)
}`,
      example: `curl -X POST "http://localhost:8000/api/stories/" \\
  -H "Content-Type: application/json" \\
  -d '{"style": "修仙", "title": "我的修仙之路"}'`
    },
    {
      method: 'GET',
      path: '/api/stories/{story_id}',
      description: '获取故事详情',
      requestBody: null,
      example: `curl "http://localhost:8000/api/stories/{story_id}"`
    },
    {
      method: 'GET',
      path: '/api/stories/{story_id}/chapters',
      description: '获取故事章节列表',
      requestBody: null,
      example: `curl "http://localhost:8000/api/stories/{story_id}/chapters"`
    },
    {
      method: 'POST',
      path: '/api/stories/{story_id}/chapters',
      description: '生成新章节',
      requestBody: null,
      example: `curl -X POST "http://localhost:8000/api/stories/{story_id}/chapters"`
    },
    {
      method: 'GET',
      path: '/api/chapters/{chapter_id}',
      description: '获取章节详情',
      requestBody: null,
      example: `curl "http://localhost:8000/api/chapters/{chapter_id}"`
    },
    {
      method: 'POST',
      path: '/api/chapters/{chapter_id}/choices',
      description: '提交用户选择并生成下一章',
      requestBody: `{
  "choice_id": "string" | null,
  "custom_choice": "string" | null
}`,
      example: `curl -X POST "http://localhost:8000/api/chapters/{chapter_id}/choices" \\
  -H "Content-Type: application/json" \\
  -d '{"choice_id": "choice_1"}'`
    }
  ]

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET':
        return 'bg-green-100 text-green-800'
      case 'POST':
        return 'bg-blue-100 text-blue-800'
      case 'PUT':
        return 'bg-yellow-100 text-yellow-800'
      case 'DELETE':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/')}
              className="flex items-center text-gray-600 hover:text-gray-800 mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              返回首页
            </button>
            
            <div className="flex items-center">
              <Code className="w-8 h-8 text-purple-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-800">API 接口文档</h1>
            </div>
          </div>
          
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Swagger UI
          </a>
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Overview */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">API 概览</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">基本信息</h3>
                <ul className="space-y-2 text-gray-600">
                  <li><strong>API 标题:</strong> AI Interactive Novel API</li>
                  <li><strong>版本:</strong> 1.0.0</li>
                  <li><strong>基础 URL:</strong> http://localhost:8000</li>
                  <li><strong>协议:</strong> HTTP/HTTPS</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">支持的故事风格</h3>
                <div className="flex flex-wrap gap-2">
                  {['修仙', '武侠', '科技'].map((style) => (
                    <span
                      key={style}
                      className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                    >
                      {style}
                    </span>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  创建故事时必须选择其中一种风格
                </p>
              </div>
            </div>
          </div>

          {/* Endpoints */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-800">API 端点</h2>
            
            {endpoints.map((endpoint, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium mr-3 ${getMethodColor(endpoint.method)}`}>
                      {endpoint.method}
                    </span>
                    <code className="text-lg font-mono text-gray-800">{endpoint.path}</code>
                  </div>
                  <button
                    onClick={() => copyToClipboard(endpoint.example, endpoint.path)}
                    className="flex items-center text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    {copiedEndpoint === endpoint.path ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
                
                <p className="text-gray-600 mb-4">{endpoint.description}</p>
                
                {endpoint.requestBody && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-800 mb-2">请求体:</h4>
                    <pre className="bg-gray-50 p-3 rounded-lg text-sm overflow-x-auto">
                      <code>{endpoint.requestBody}</code>
                    </pre>
                  </div>
                )}
                
                <div>
                  <h4 className="text-sm font-medium text-gray-800 mb-2">示例:</h4>
                  <pre className="bg-gray-900 text-green-400 p-3 rounded-lg text-sm overflow-x-auto">
                    <code>{endpoint.example}</code>
                  </pre>
                </div>
              </div>
            ))}
          </div>

          {/* Response Format */}
          <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">响应格式</h2>
            <p className="text-gray-600 mb-4">所有 API 响应都遵循统一的格式：</p>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">成功响应</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">
                  <code>{`{
  "success": true,
  "data": {
    // 具体的数据内容
  },
  "message": "操作成功" // 可选
}`}</code>
                </pre>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">错误响应</h3>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto">
                  <code>{`{
  "success": false,
  "data": null,
  "message": "错误描述"
}`}</code>
                </pre>
              </div>
            </div>
          </div>

          {/* Status Codes */}
          <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">HTTP 状态码</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="w-12 h-8 bg-green-100 text-green-800 rounded text-sm font-medium flex items-center justify-center mr-3">
                    200
                  </span>
                  <span className="text-gray-700">请求成功</span>
                </div>
                <div className="flex items-center">
                  <span className="w-12 h-8 bg-yellow-100 text-yellow-800 rounded text-sm font-medium flex items-center justify-center mr-3">
                    422
                  </span>
                  <span className="text-gray-700">请求参数验证失败</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="w-12 h-8 bg-red-100 text-red-800 rounded text-sm font-medium flex items-center justify-center mr-3">
                    404
                  </span>
                  <span className="text-gray-700">资源不存在</span>
                </div>
                <div className="flex items-center">
                  <span className="w-12 h-8 bg-red-100 text-red-800 rounded text-sm font-medium flex items-center justify-center mr-3">
                    500
                  </span>
                  <span className="text-gray-700">服务器内部错误</span>
                </div>
              </div>
            </div>
          </div>

          {/* Usage Notes */}
          <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">使用说明</h2>
            <div className="space-y-4 text-gray-600">
              <div className="flex items-start">
                <Book className="w-5 h-5 text-purple-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <strong className="text-gray-800">故事创建流程：</strong>
                  <p>1. 使用 POST /api/stories/ 创建故事</p>
                  <p>2. 使用 POST /api/stories/&#123;story_id&#125;/chapters 生成第一章</p>
                  <p>3. 使用 POST /api/chapters/&#123;chapter_id&#125;/choices 提交选择生成后续章节</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <Code className="w-5 h-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <strong className="text-gray-800">编码要求：</strong>
                  <p>所有请求和响应都使用 UTF-8 编码，支持中文内容</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <ExternalLink className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <strong className="text-gray-800">交互式文档：</strong>
                  <p>访问 <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">http://localhost:8000/docs</a> 查看 Swagger UI 并直接测试 API</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}