import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, BookOpen, ChevronRight, Plus, Send } from 'lucide-react'

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
  const [story, setStory] = useState<Story | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [customChoice, setCustomChoice] = useState('')
  const [showCustomInput, setShowCustomInput] = useState(false)

  useEffect(() => {
    if (storyId) {
      loadStory()
      loadChapters()
    }
  }, [storyId])

  const loadStory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/stories/${storyId}`)
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
      const response = await fetch(`http://localhost:8000/api/stories/${storyId}/chapters`)
      const result = await response.json()
      if (result.success && result.data) {
        setChapters(result.data)
        if (result.data.length > 0) {
          setCurrentChapter(result.data[result.data.length - 1])
        }
      }
    } catch (error) {
      console.error('加载章节失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateFirstChapter = async () => {
    setGenerating(true)
    try {
      const response = await fetch(`http://localhost:8000/api/stories/${storyId}/chapters`, {
        method: 'POST'
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
    try {
      const response = await fetch(`http://localhost:8000/api/chapters/${currentChapter.id}/choices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          choice_id: choiceId || null,
          custom_choice: customText || null
        })
      })

      const result = await response.json()
      if (result.success) {
        await loadChapters()
        setCustomChoice('')
        setShowCustomInput(false)
      } else {
        alert('提交选择失败：' + result.message)
      }
    } catch (error) {
      alert('提交选择失败：' + error)
    } finally {
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-800 mr-4"
          >
            <ArrowLeft className="w-5 h-5 mr-1" />
            返回首页
          </button>
          
          {story && (
            <div className="flex items-center">
              <BookOpen className="w-6 h-6 text-purple-600 mr-2" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{story.title}</h1>
                <p className="text-sm text-gray-600">风格：{story.style}</p>
              </div>
            </div>
          )}
        </div>

        <div className="max-w-4xl mx-auto">
          {chapters.length === 0 ? (
            /* No chapters yet */
            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
              <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">故事即将开始</h2>
              <p className="text-gray-600 mb-6">点击下方按钮生成第一章</p>
              <button
                onClick={generateFirstChapter}
                disabled={generating}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {generating ? '生成中...' : '开始故事'}
              </button>
            </div>
          ) : (
            /* Story content */
            <div className="space-y-6">
              {/* Chapter list */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">章节列表</h2>
                <div className="space-y-2">
                  {chapters.map((chapter, index) => (
                    <button
                      key={chapter.id}
                      onClick={() => setCurrentChapter(chapter)}
                      className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                        currentChapter?.id === chapter.id
                          ? 'bg-purple-100 border-2 border-purple-300'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-800">
                            第{chapter.chapter_number}章 {chapter.title}
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Current chapter content */}
              {currentChapter && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    第{currentChapter.chapter_number}章 {currentChapter.title}
                  </h2>
                  
                  <div className="prose max-w-none mb-6">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {currentChapter.content}
                    </div>
                  </div>

                  {/* Choices */}
                  {currentChapter.choices && currentChapter.choices.length > 0 && (
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">选择你的行动：</h3>
                      
                      <div className="space-y-3">
                        {currentChapter.choices.map((choice) => (
                          <button
                            key={choice.id}
                            onClick={() => handleChoice(choice.id)}
                            disabled={generating}
                            className="w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <div className="font-medium text-blue-800">{choice.text}</div>
                          </button>
                        ))}
                        
                        {/* Custom choice */}
                        <div className="border-t pt-4">
                          {!showCustomInput ? (
                            <button
                              onClick={() => setShowCustomInput(true)}
                              className="flex items-center text-green-600 hover:text-green-700 font-medium"
                            >
                              <Plus className="w-4 h-4 mr-1" />
                              自定义选择
                            </button>
                          ) : (
                            <div className="space-y-3">
                              <textarea
                                value={customChoice}
                                onChange={(e) => setCustomChoice(e.target.value)}
                                placeholder="输入你的自定义选择..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                rows={3}
                              />
                              <div className="flex space-x-2">
                                <button
                                  onClick={handleCustomChoice}
                                  disabled={generating || !customChoice.trim()}
                                  className="flex items-center bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                  <Send className="w-4 h-4 mr-1" />
                                  提交选择
                                </button>
                                <button
                                  onClick={() => {
                                    setShowCustomInput(false)
                                    setCustomChoice('')
                                  }}
                                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                                >
                                  取消
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {generating && (
                        <div className="mt-4 text-center">
                          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto mb-2"></div>
                          <p className="text-gray-600">正在生成下一章...</p>
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
    </div>
  )
}