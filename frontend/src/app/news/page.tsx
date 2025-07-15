'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { newsApi, aiApi, type NewsArticle } from '@/lib/api'
import { formatRelativeTime, truncateText } from '@/lib/utils'
import { useWebSocket } from '../providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Newspaper,
  Search,
  Filter,
  TrendingUp,
  Clock,
  ExternalLink,
  Brain,
  Sparkles,
  AlertCircle,
  RefreshCw,
  Eye,
  MessageSquare,
  Share2,
  BookmarkPlus
} from 'lucide-react'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface NewsAnalysisModalProps {
  article: NewsArticle | null
  isOpen: boolean
  onClose: () => void
}

function NewsAnalysisModal({ article, isOpen, onClose }: NewsAnalysisModalProps) {
  const [analysis, setAnalysis] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (article && isOpen) {
      analyzeArticle()
    }
  }, [article, isOpen])

  const analyzeArticle = async () => {
    if (!article?.content) return
    
    setIsLoading(true)
    try {
      const response = await newsApi.analyzeSentiment(article.content)
      setAnalysis(response.data.analysis || 'Analysis not available')
    } catch (error) {
      setAnalysis('Failed to analyze article sentiment')
    } finally {
      setIsLoading(false)
    }
  }

  if (!article || !isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-500" />
              AI News Analysis
            </h3>
            <Button variant="ghost" size="sm" onClick={onClose}>×</Button>
          </div>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-8rem)]">
          <div className="space-y-6">
            {/* Article Info */}
            <div>
              <h4 className="font-semibold text-lg mb-2">{article.title}</h4>
              <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                <span>{article.source?.name}</span>
                <span>{formatRelativeTime(article.publishedAt || '')}</span>
                {article.url && (
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-blue-600 hover:underline"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Original
                  </a>
                )}
              </div>
            </div>

            {/* Article Image */}
            {article.urlToImage && (
              <div className="rounded-lg overflow-hidden">
                <img 
                  src={article.urlToImage} 
                  alt={article.title || ''}
                  className="w-full h-48 object-cover"
                />
              </div>
            )}

            {/* Article Description */}
            {article.description && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-gray-700 dark:text-gray-300">{article.description}</p>
              </div>
            )}

            {/* AI Analysis */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
              <h5 className="font-semibold flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-purple-500" />
                AI Sentiment Analysis
              </h5>
              {isLoading ? (
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Analyzing article sentiment...
                </div>
              ) : (
                <p className="text-gray-700 dark:text-gray-300">{analysis}</p>
              )}
            </div>

            {/* Market Impact */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <h5 className="font-semibold flex items-center gap-2 mb-3">
                <TrendingUp className="w-4 h-4 text-yellow-600" />
                Potential Market Impact
              </h5>
              <p className="text-gray-700 dark:text-gray-300">
                This news could influence prediction markets related to {article.category || 'the topic'}. 
                Consider monitoring related markets for trading opportunities.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default function NewsPage() {
  const { connected } = useWebSocket()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null)
  const [isAnalysisModalOpen, setIsAnalysisModalOpen] = useState(false)
  
  // Fetch data with SWR
  const { data: trendingNews = [], mutate: mutateTrending } = useSWR(
    'trending-news',
    () => newsApi.getTrendingNews({ limit: 20 }).then(res => res.data.articles),
    { refreshInterval: 300000 } // 5 minutes
  )

  const { data: allNews = [], mutate: mutateAll } = useSWR(
    ['news', selectedCategory],
    () => selectedCategory === 'all' 
      ? newsApi.getNews({ limit: 30 }).then(res => res.data.articles)
      : newsApi.getCategoryNews(selectedCategory, { limit: 30 }).then(res => res.data.articles),
    { refreshInterval: 300000 }
  )

  // Filter news based on search
  const filteredNews = allNews.filter((article: NewsArticle) => {
    if (!searchTerm) return true
    return article.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
           article.description?.toLowerCase().includes(searchTerm.toLowerCase())
  })

  const categories = ['all', 'politics', 'sports', 'crypto', 'entertainment', 'tech', 'business']

  const handleAnalyzeClick = (article: NewsArticle) => {
    setSelectedArticle(article)
    setIsAnalysisModalOpen(true)
  }

  const refreshNews = () => {
    mutateTrending()
    mutateAll()
    toast.success('News refreshed!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                News & Analysis
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Stay updated with market-moving news and AI-powered insights
              </p>
            </div>
            <Button onClick={refreshNews} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main News Feed */}
          <div className="lg:col-span-3">
            {/* Filters */}
            <Card className="mb-6">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search news..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {categories.map((cat) => (
                      <Button
                        key={cat}
                        variant={selectedCategory === cat ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedCategory(cat)}
                        className="capitalize"
                      >
                        {cat === 'all' ? 'All' : cat}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* News Articles */}
            <div className="space-y-6">
              <AnimatePresence>
                {filteredNews.map((article: NewsArticle, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="hover:shadow-md transition-all duration-200">
                      <CardContent className="p-6">
                        <div className="flex gap-4">
                          {/* Article Image */}
                          <div className="w-32 h-24 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                            {article.urlToImage ? (
                              <img 
                                src={article.urlToImage} 
                                alt=""
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                                <Newspaper className="w-8 h-8 text-gray-400" />
                              </div>
                            )}
                          </div>

                          {/* Article Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between mb-2">
                              <h3 className="font-semibold text-lg text-gray-900 dark:text-white line-clamp-2">
                                {article.title}
                              </h3>
                              <div className="flex items-center gap-2 ml-4">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleAnalyzeClick(article)}
                                >
                                  <Brain className="w-4 h-4 mr-1" />
                                  Analyze
                                </Button>
                              </div>
                            </div>
                            
                            <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 line-clamp-2">
                              {article.description}
                            </p>
                            
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4 text-xs text-gray-500">
                                <span className="flex items-center gap-1">
                                  <span>{article.source?.name}</span>
                                </span>
                                <span className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {formatRelativeTime(article.publishedAt || '')}
                                </span>
                                {article.category && (
                                  <Badge variant="secondary" className="text-xs">
                                    {article.category}
                                  </Badge>
                                )}
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <Button size="sm" variant="ghost">
                                  <BookmarkPlus className="w-4 h-4" />
                                </Button>
                                <Button size="sm" variant="ghost">
                                  <Share2 className="w-4 h-4" />
                                </Button>
                                {article.url && (
                                  <Button size="sm" variant="ghost" asChild>
                                    <a 
                                      href={article.url} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                    >
                                      <ExternalLink className="w-4 h-4" />
                                    </a>
                                  </Button>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {filteredNews.length === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No news articles found</p>
              </div>
            )}
          </div>

          {/* Sidebar - Trending News */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-orange-500" />
                  Trending Now
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {trendingNews.slice(0, 6).map((article: NewsArticle, index: number) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="group cursor-pointer"
                      onClick={() => handleAnalyzeClick(article)}
                    >
                      <div className="flex gap-3">
                        <div className="w-12 h-12 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                          {article.urlToImage ? (
                            <img 
                              src={article.urlToImage} 
                              alt=""
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                            />
                          ) : (
                            <div className="w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                              <Newspaper className="w-4 h-4 text-gray-400" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 transition-colors">
                            {truncateText(article.title || '', 60)}
                          </h4>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatRelativeTime(article.publishedAt || '')}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-500" />
                  AI Market Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Sparkles className="w-4 h-4 text-purple-500 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-purple-900 dark:text-purple-100">Market Sentiment</p>
                        <p className="text-purple-700 dark:text-purple-300">Bullish sentiment detected in crypto markets</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-blue-900 dark:text-blue-100">Trending Topics</p>
                        <p className="text-blue-700 dark:text-blue-300">Election markets showing increased activity</p>
                      </div>
                    </div>
                  </div>
                </div>
                <Button className="w-full mt-4" variant="outline">
                  View Full Analysis
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* News Analysis Modal */}
      <AnimatePresence>
        {isAnalysisModalOpen && (
          <NewsAnalysisModal
            article={selectedArticle}
            isOpen={isAnalysisModalOpen}
            onClose={() => setIsAnalysisModalOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}