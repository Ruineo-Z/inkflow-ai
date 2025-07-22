import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Book, Calendar, Tag, ChevronRight } from 'lucide-react'

interface Story {
  id: string
  title: string
  style: string
  created_at: string
  chapter_count?: number
}

export default function Stories() {
  const navigate = useNavigate()
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    loadStories()
  }, [])

  const loadStories = async () => {
    try {
      // Note: This endpoint doesn't exist in the API, so we'll simulate it
      // In a real implementation, you'd need to add this endpoint to the backend
      setStories([
        {
          id: '1',
          title: '修仙传奇',
          style: '修仙',
          created_at: '2024-01-15T10:30:00Z',
          chapter_count: 5
        },
        {
          id: '2', 
          title: '江湖恩仇',
          style: '武侠',
          created_at: '2024-01-14T15:20:00Z',
          chapter_count: 3
        },
        {
          id: '3',
          title: '星际探索',
          style: '科技',
          created_at: '2024-01-13T09:45:00Z',
          chapter_count: 7
        }
      ])
    } catch (error) {
      console.error('加载故事列表失败:', error)
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

  const getStyleColor = (style: string) => {
    switch (style) {
      case '修仙':
        return 'bg-purple-100 text-purple-800'
      case '武侠':
        return 'bg-red-100 text-red-800'
      case '科技':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
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
              <Book className="w-8 h-8 text-purple-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-800">故事列表</h1>
            </div>
          </div>
          
          <button
            onClick={() => navigate('/')}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all"
          >
            创建新故事
          </button>
        </div>

        <div className="max-w-6xl mx-auto">
          {/* Filter */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">筛选故事</h2>
            <div className="flex flex-wrap gap-2">
              {['all', '修仙', '武侠', '科技'].map((styleOption) => (
                <button
                  key={styleOption}
                  onClick={() => setFilter(styleOption)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === styleOption
                      ? 'bg-purple-600 text-white'
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
            <div className="bg-white rounded-xl shadow-lg p-12 text-center">
              <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">暂无故事</h2>
              <p className="text-gray-600 mb-6">
                {filter === 'all' ? '还没有创建任何故事' : `没有找到${filter}风格的故事`}
              </p>
              <button
                onClick={() => navigate('/')}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all"
              >
                创建第一个故事
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStories.map((story) => (
                <div
                  key={story.id}
                  className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
                  onClick={() => navigate(`/story/${story.id}`)}
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-xl font-semibold text-gray-800 line-clamp-2">
                        {story.title}
                      </h3>
                      <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" />
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center">
                        <Tag className="w-4 h-4 text-gray-500 mr-2" />
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStyleColor(story.style)}`}>
                          {story.style}
                        </span>
                      </div>
                      
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {formatDate(story.created_at)}
                      </div>
                      
                      {story.chapter_count !== undefined && (
                        <div className="flex items-center text-sm text-gray-600">
                          <Book className="w-4 h-4 mr-2" />
                          {story.chapter_count} 章节
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-4 pt-4 border-t">
                      <button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-2 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all">
                        继续阅读
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Stats */}
          {filteredStories.length > 0 && (
            <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">统计信息</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{stories.length}</div>
                  <div className="text-sm text-gray-600">总故事数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {stories.reduce((sum, story) => sum + (story.chapter_count || 0), 0)}
                  </div>
                  <div className="text-sm text-gray-600">总章节数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {stories.filter(s => s.style === '修仙').length}
                  </div>
                  <div className="text-sm text-gray-600">修仙故事</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
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