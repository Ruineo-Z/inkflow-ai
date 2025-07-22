import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Book, Plus, List, Heart } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()
  const [isCreating, setIsCreating] = useState(false)
  const [title, setTitle] = useState('')
  const [style, setStyle] = useState<'修仙' | '武侠' | '科技'>('修仙')

  const handleCreateStory = async () => {
    if (!title.trim()) {
      alert('请输入故事标题')
      return
    }

    setIsCreating(true)
    try {
      const response = await fetch('http://localhost:8000/api/stories/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Book className="w-12 h-12 text-purple-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">AI交互式小说</h1>
          </div>
          <p className="text-gray-600 text-lg">开启你的专属冒险故事</p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Create New Story */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <Plus className="w-6 h-6 text-green-600 mr-2" />
                <h2 className="text-2xl font-semibold text-gray-800">创建新故事</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    故事标题
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="输入你的故事标题..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          style === styleOption
                            ? 'bg-purple-600 text-white'
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
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isCreating ? '创建中...' : '开始冒险'}
                </button>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-4">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center mb-4">
                  <List className="w-6 h-6 text-blue-600 mr-2" />
                  <h2 className="text-2xl font-semibold text-gray-800">快速操作</h2>
                </div>
                
                <div className="space-y-3">
                  <button
                    onClick={() => navigate('/stories')}
                    className="w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                  >
                    <div className="font-medium text-blue-800">浏览所有故事</div>
                    <div className="text-sm text-blue-600">查看已创建的故事列表</div>
                  </button>
                  
                  <button
                    onClick={() => navigate('/api-docs')}
                    className="w-full text-left px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                  >
                    <div className="font-medium text-green-800">API文档</div>
                    <div className="text-sm text-green-600">查看完整的API接口文档</div>
                  </button>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center mb-4">
                  <Heart className="w-6 h-6 text-red-600 mr-2" />
                  <h2 className="text-xl font-semibold text-gray-800">功能特色</h2>
                </div>
                
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                    AI智能生成故事内容
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-blue-400 rounded-full mr-3"></span>
                    多种故事风格选择
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
                    交互式选择推进剧情
                  </li>
                  <li className="flex items-center">
                    <span className="w-2 h-2 bg-red-400 rounded-full mr-3"></span>
                    自定义选择选项
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}