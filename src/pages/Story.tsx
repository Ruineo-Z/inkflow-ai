import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Book, BookOpen, ChevronRight, Plus, Send } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface Chapter {
  id: string
  chapter_number: number
  title: string
  content: string
  choices: Choice[]
}

interface Choice {
  id: string
  text: string
}

interface Story {
  id: string
  title: string
  style: string
  created_at: string
}

export default function Story() {
  const { storyId } = useParams<{ storyId: string }>()
  const navigate = useNavigate()
  const { token } = useAuthStore()
  const [story, setStory] = useState<Story | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [customChoice, setCustomChoice] = useState('')
  const [showCustomInput, setShowCustomInput] = useState(false)
  const [streamingContent, setStreamingContent] = useState({ title: '', content: '' })
  const [isStreaming, setIsStreaming] = useState(false)

  useEffect(() => {
    if (storyId) {
      loadStory()
      loadChapters()
    }
  }, [storyId])

  const loadStory = async () => {
    try {
      const response = await fetch(`http://localhost:20001/api/stories/${storyId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      if (result.success) {
        setStory(result.data)
      }
    } catch (error) {
      console.error('加载故事失败:', error)
    }
  }

  const loadChapters = async () => {
    try {
      const response = await fetch(`http://localhost:20001/api/stories/${storyId}/chapters`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      console.log('章节API响应:', result) // 添加调试日志
      if (result.success && result.data && result.data.chapters && Array.isArray(result.data.chapters)) {
        setChapters(result.data.chapters)
        if (result.data.chapters.length > 0) {
          setCurrentChapter(result.data.chapters[result.data.chapters.length - 1])
        }
      } else {
        // 确保 chapters 始终是数组
        console.warn('API 返回的数据格式不正确:', result)
        setChapters([])
      }
    } catch (error) {
      console.error('加载章节失败:', error)
      // 确保 chapters 始终是数组
      setChapters([])
    } finally {
      setLoading(false)
    }
  }

  const generateFirstChapter = async () => {
    setGenerating(true)
    try {
      const response = await fetch(`http://localhost:20001/api/stories/${storyId}/chapters`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      if (result.success) {
        await loadChapters()
      } else {
        alert('生成章节失败：' + result.message)
      }
    } catch (error) {
      alert('生成章节失败：' + error)
    } finally {
      setGenerating(false)
    }
  }

  const handleChoice = async (choiceId?: string, customText?: string) => {
    if (!currentChapter) return

    setGenerating(true)
    setIsStreaming(true)
    setStreamingContent({ title: '', content: '' })
    
    try {
      // 构建请求体
      const requestBody: any = {}
      if (choiceId) {
        requestBody.choice_id = choiceId
      }
      if (customText) {
        requestBody.custom_choice = customText
      }
      
      // 使用 fetch 进行流式请求
      const response = await fetch(`http://localhost:20001/api/chapters/stream/${currentChapter.id}/choices`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法获取响应流')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'title') {
                setStreamingContent(prev => ({ ...prev, title: data.content }))
              } else if (data.type === 'content') {
                setStreamingContent(prev => ({ ...prev, content: prev.content + data.content }))
              } else if (data.type === 'complete') {
                setIsStreaming(false)
                setStreamingContent({ title: '', content: '' })
                // 重新加载章节数据
                await loadChapters()
                setCustomChoice('')
                setShowCustomInput(false)
                setGenerating(false)
                return
              } else if (data.type === 'error') {
                console.error('生成错误:', data.message)
                alert('生成章节失败：' + data.message)
                setIsStreaming(false)
                setStreamingContent({ title: '', content: '' })
                setGenerating(false)
                return
              }
            } catch (parseError) {
              console.error('解析响应数据失败:', parseError)
            }
          }
        }
      }

    } catch (error) {
      console.error('提交选择失败:', error)
      alert('提交选择失败：' + error)
      setIsStreaming(false)
      setStreamingContent({ title: '', content: '' })
      setGenerating(false)
    }
  }

  const handleCustomChoice = () => {
    if (customChoice.trim()) {
      handleChoice(undefined, customChoice.trim())
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-1" />
              返回首页
            </button>
            <button
              onClick={() => navigate('/stories')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Book className="w-5 h-5 mr-1" />
              故事列表
            </button>
          </div>
          
          {story && (
            <div>
              <h1 className="text-xl font-semibold text-gray-900">{story.title}</h1>
              <p className="text-sm text-gray-600">{story.style}</p>
            </div>
          )}
        </div>

        <div className="max-w-4xl mx-auto">
          {!Array.isArray(chapters) || chapters.length === 0 ? (
            /* No chapters yet */
            <div className="bg-white rounded-lg border p-8 text-center">
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">故事即将开始</h2>
              <p className="text-gray-600 mb-6">点击下方按钮生成第一章</p>
              <button
                onClick={generateFirstChapter}
                disabled={generating}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {generating ? '生成中...' : '开始故事'}
              </button>
            </div>
          ) : (
            /* Story content */
            <div className="flex flex-col lg:flex-row gap-6">
              {/* Left sidebar - Chapter list */}
              <div className="lg:w-80 lg:flex-shrink-0">
                <div className="bg-white rounded-lg border p-4 lg:sticky lg:top-4">
                  <h2 className="text-lg font-semibold text-gray-900 mb-3">章节列表</h2>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {Array.isArray(chapters) && chapters.map((chapter, index) => (
                      <button
                        key={chapter.id}
                        onClick={() => setCurrentChapter(chapter)}
                        className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                          currentChapter?.id === chapter.id
                            ? 'bg-blue-100 border border-blue-300'
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-medium text-gray-900 text-sm">
                            第{chapter.chapter_number}章 {chapter.title}
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right main content - Current chapter */}
              <div className="flex-1">
              {currentChapter && (
                <div className="bg-white rounded-lg border p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    第{currentChapter.chapter_number}章 {currentChapter.title}
                  </h2>
                  
                  <div className="mb-6">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {currentChapter.content}
                    </div>
                  </div>

                  {/* Choices */}
                  {currentChapter.choices && Array.isArray(currentChapter.choices) && currentChapter.choices.length > 0 && (
                    <div className="border-t pt-4">
                      <h3 className="text-base font-medium text-gray-900 mb-3">选择你的行动：</h3>
                      
                      <div className="space-y-2">
                        {Array.isArray(currentChapter.choices) && currentChapter.choices.map((choice) => (
                          <button
                            key={choice.id}
                            onClick={() => handleChoice(choice.id)}
                            disabled={generating}
                            className="w-full text-left px-3 py-2 border border-gray-200 hover:bg-gray-50 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <div className="text-gray-900">{choice.text}</div>
                          </button>
                        ))}
                        
                        {/* Custom choice */}
                        <div className="border-t pt-3 mt-3">
                          {!showCustomInput ? (
                            <button
                              onClick={() => setShowCustomInput(true)}
                              className="flex items-center text-blue-600 hover:text-blue-700 text-sm"
                            >
                              <Plus className="w-4 h-4 mr-1" />
                              自定义选择
                            </button>
                          ) : (
                            <div className="space-y-2">
                              <textarea
                                value={customChoice}
                                onChange={(e) => setCustomChoice(e.target.value)}
                                placeholder="输入你的自定义选择..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                rows={2}
                              />
                              <div className="flex space-x-2">
                                <button
                                  onClick={handleCustomChoice}
                                  disabled={generating || !customChoice.trim()}
                                  className="flex items-center bg-blue-600 text-white px-3 py-1 text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                  <Send className="w-3 h-3 mr-1" />
                                  提交
                                </button>
                                <button
                                  onClick={() => {
                                    setShowCustomInput(false)
                                    setCustomChoice('')
                                  }}
                                  className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
                                >
                                  取消
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {generating && (
                        <div className="mt-4">
                          <div className="text-center mb-3">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mx-auto mb-2"></div>
                            <p className="text-sm text-gray-600">正在生成下一章...</p>
                          </div>
                          
                          {/* 流式内容显示 */}
                          {isStreaming && (streamingContent.title || streamingContent.content) && (
                            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                              <h4 className="text-sm font-medium text-blue-800 mb-2">正在生成中...</h4>
                              {streamingContent.title && (
                                <div className="mb-2">
                                  <span className="text-xs text-blue-600 font-medium">标题：</span>
                                  <span className="text-sm text-blue-800">{streamingContent.title}</span>
                                </div>
                              )}
                              {streamingContent.content && (
                                <div>
                                  <span className="text-xs text-blue-600 font-medium">内容：</span>
                                  <div className="text-sm text-blue-800 whitespace-pre-wrap mt-1">
                                    {streamingContent.content}
                                    <span className="animate-pulse">|</span>
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}