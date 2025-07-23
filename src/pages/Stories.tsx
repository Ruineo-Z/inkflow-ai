import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Book, ChevronRight } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface Story {
  id: string
  title: string
  style: string
  created_at: string
  chapter_count?: number
}

export default function Stories() {
  const navigate = useNavigate()
  const { token } = useAuthStore()
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    loadStories()
  }, [])

  const loadStories = async () => {
    try {
      const response = await fetch('http://localhost:20001/api/stories', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      const result = await response.json()
      if (result.success && Array.isArray(result.data)) {
        // Transform the data to match our interface
        const transformedStories = result.data.map((story: any) => ({
          id: story.id.toString(),
          title: story.title,
          style: story.style,
          created_at: story.created_at,
          chapter_count: story.chapter_count || 0
        }))
        setStories(transformedStories)
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }



  const filteredStories = stories.filter(story => {
    if (filter === 'all') return true
    return story.style === filter
  })

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
              <Book className="w-8 h-8 text-purple-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-800">故事列表</h1>
            </div>
          </div>
          
          <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors"
            >
              创建新故事
            </button>
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Filter */}
          <div className="bg-white rounded-lg border p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">筛选故事</h2>
            <div className="flex flex-wrap gap-2">
              {['all', '修仙', '武侠', '科技'].map((styleOption) => (
                <button
                  key={styleOption}
                  onClick={() => setFilter(styleOption)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filter === styleOption
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {styleOption === 'all' ? '全部' : styleOption}
                </button>
              ))}
            </div>
          </div>

          {/* Stories Grid */}
          {filteredStories.length === 0 ? (
            <div className="bg-white rounded-lg border p-12 text-center">
              <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">暂无故事</h2>
              <p className="text-gray-600 mb-6">
                {filter === 'all' ? '还没有创建任何故事' : `没有找到${filter}风格的故事`}
              </p>
              <button
                onClick={() => navigate('/')}
                className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors"
              >
                创建第一个故事
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredStories.map((story) => (
                <button
                  key={story.id}
                  onClick={() => navigate(`/story/${story.id}`)}
                  className="w-full text-left p-3 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors bg-white"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{story.title}</div>
                      <div className="text-sm text-gray-600">
                        {story.style} · {formatDate(story.created_at)}
                        {story.chapter_count !== undefined && ` · ${story.chapter_count} 章节`}
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" />
                  </div>
                </button>
              ))}
            </div>
          )}
          
          {/* Stats */}
          {filteredStories.length > 0 && (
            <div className="mt-6 bg-white rounded-lg border p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">统计信息</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{stories.length}</div>
                  <div className="text-sm text-gray-600">总故事数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {stories.reduce((sum, story) => sum + (story.chapter_count || 0), 0)}
                  </div>
                  <div className="text-sm text-gray-600">总章节数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {stories.filter(s => s.style === '修仙').length}
                  </div>
                  <div className="text-sm text-gray-600">修仙故事</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {stories.filter(s => s.style === '武侠').length}
                  </div>
                  <div className="text-sm text-gray-600">武侠故事</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}