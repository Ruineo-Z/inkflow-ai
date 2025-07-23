import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, LogOut, ArrowLeft, Copy, CheckCircle, Book } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

export default function UserCenter() {
  const navigate = useNavigate()
  const { user, logout, isAuthenticated } = useAuthStore()
  const [copied, setCopied] = useState(false)
  const [stories, setStories] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    loadUserStories()
  }, [isAuthenticated, navigate])

  const loadUserStories = async () => {
    try {
      const response = await fetch('http://localhost:20001/api/stories/', {
        headers: {
          'Authorization': `Bearer ${useAuthStore.getState().token}`
        }
      })
      const result = await response.json()
      if (result.success && Array.isArray(result.data)) {
        setStories(result.data)
      }
    } catch (error) {
      console.error('加载故事列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const copyUserId = () => {
    if (user?.user_id) {
      navigator.clipboard.writeText(user.user_id)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回首页
          </button>
          <h1 className="text-2xl font-bold text-gray-900">用户中心</h1>
          <div className="w-20"></div>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {/* User Info */}
            <div className="bg-white rounded-lg border p-6">
              <div className="flex items-center mb-6">
                <User className="w-8 h-8 text-blue-600 mr-3" />
                <h2 className="text-xl font-semibold text-gray-900">个人信息</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    用户名
                  </label>
                  <div className="px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
                    {user.username}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    用户ID
                  </label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-mono">
                      {user.user_id}
                    </div>
                    <button
                      onClick={copyUserId}
                      className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {copied ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <Copy className="w-5 h-5 text-gray-600" />
                      )}
                    </button>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    这是您的登录凭证，请妥善保存
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    注册时间
                  </label>
                  <div className="px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
                    {formatDate(user.created_at)}
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="w-full flex justify-center items-center py-2 px-4 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  退出登录
                </button>
              </div>
            </div>

            {/* User Stories */}
            <div className="bg-white rounded-lg border p-6">
              <div className="flex items-center mb-6">
                <Book className="w-8 h-8 text-blue-600 mr-3" />
                <h2 className="text-xl font-semibold text-gray-900">我的故事</h2>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  <p className="text-gray-600">加载中...</p>
                </div>
              ) : stories.length === 0 ? (
                <div className="text-center py-8">
                  <Book className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600 mb-4">还没有创建任何故事</p>
                  <button
                    onClick={() => navigate('/')}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    去创建第一个故事
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="text-sm text-gray-600 mb-4">
                    共 {stories.length} 个故事
                  </div>
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