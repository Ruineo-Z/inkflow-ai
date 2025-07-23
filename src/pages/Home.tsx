import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Book, Plus, List, User, LogIn, UserPlus } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface Story {
  id: string
  title: string
  style: string
  created_at: string
}

export default function Home() {
  const navigate = useNavigate()
  const { user, isAuthenticated, token } = useAuthStore()
  const [isCreating, setIsCreating] = useState(false)
  const [title, setTitle] = useState('')
  const [style, setStyle] = useState<'修仙' | '武侠' | '科技'>('修仙')
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStories()
  }, [])

  const loadStories = async () => {
    try {
      const headers: any = {}
      if (isAuthenticated && token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await fetch('http://localhost:20001/api/stories/', {
        headers
      })
      const result = await response.json()
      if (result.success && Array.isArray(result.data)) {
        setStories(result.data)
      } else {
        setStories([])
      }
    } catch (error) {
      console.error('加载故事列表失败:', error)
      setStories([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStory = async () => {
    if (!isAuthenticated) {
      alert('请先登录后再创建故事')
      navigate('/login')
      return
    }

    if (!title.trim()) {
      alert('请输入故事标题')
      return
    }

    setIsCreating(true)
    try {
      const response = await fetch('http://localhost:20001/api/stories/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: title.trim(),
          style: style
        })
      })

      const result = await response.json()
      if (result.success) {
        navigate(`/story/${result.data.id}`)
      } else {
        alert('创建故事失败：' + result.message)
      }
    } catch (error) {
      alert('创建故事失败：' + error)
    } finally {
      setIsCreating(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2 text-center">AI交互式小说</h1>
            <p className="text-gray-600 text-center">创建和阅读你的专属故事</p>
          </div>
          
          {/* User Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">欢迎，{user?.username}</span>
                <button
                  onClick={() => navigate('/user-center')}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <User className="w-4 h-4 mr-2" />
                  用户中心
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => navigate('/login')}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <LogIn className="w-4 h-4 mr-2" />
                  登录
                </button>
                <button
                  onClick={() => navigate('/register')}
                  className="flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  注册
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Create New Story */}
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">创建新故事</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    故事标题
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="输入故事标题"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    故事风格
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['修仙', '武侠', '科技'] as const).map((styleOption) => (
                      <button
                        key={styleOption}
                        onClick={() => setStyle(styleOption)}
                        className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                          style === styleOption
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {styleOption}
                      </button>
                    ))}
                  </div>
                </div>
                
                <button
                  onClick={handleCreateStory}
                  disabled={isCreating || !title.trim()}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isCreating ? '创建中...' : (isAuthenticated ? '创建故事' : '登录后创建故事')}
                </button>
              </div>
            </div>

            {/* Read Stories */}
            <div className="bg-white rounded-lg border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">我的故事</h2>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  <p className="text-gray-600">加载中...</p>
                </div>
              ) : stories.length === 0 ? (
                <div className="text-center py-8">
                  <Book className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">还没有创建任何故事</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {stories.slice(0, 5).map((story) => (
                    <button
                      key={story.id}
                      onClick={() => navigate(`/story/${story.id}`)}
                      className="w-full text-left p-3 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                    >
                      <div className="font-medium text-gray-900">{story.title}</div>
                      <div className="text-sm text-gray-600">
                        {story.style} · {formatDate(story.created_at)}
                      </div>
                    </button>
                  ))}
                  
                  {stories.length > 5 && (
                    <button
                      onClick={() => navigate('/stories')}
                      className="w-full text-center py-2 text-blue-600 hover:text-blue-700 font-medium"
                    >
                      查看全部 ({stories.length} 个故事)
                    </button>
                  )}
                  
                  {stories.length <= 5 && stories.length > 0 && (
                    <button
                      onClick={() => navigate('/stories')}
                      className="w-full text-center py-2 text-blue-600 hover:text-blue-700 font-medium"
                    >查看全部故事</button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}