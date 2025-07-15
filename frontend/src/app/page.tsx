'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { marketApi, newsApi, aiApi, type Market, type NewsArticle } from '@/lib/api'
import { 
  formatPrice, 
  formatPercentage, 
  getCategoryColor, 
  getCategoryIcon, 
  formatRelativeTime, 
  truncateText,
  formatCompactNumber,
  getMarketStatusColor,
  getMarketStatusText
} from '@/lib/utils'
import { useWebSocket } from './providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TrendingUp, 
  Activity, 
  Brain, 
  NewspaperIcon, 
  Target, 
  Zap,
  Search,
  Filter,
  ChevronRight,
  DollarSign,
  Users,
  Clock,
  AlertCircle,
  Star,
  Play,
  TrendingDown
} from 'lucide-react'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface DashboardStats {
  totalMarkets: number
  activeMarkets: number
  totalVolume: number
  avgSpread: number
}

export default function Dashboard() {
  const { connected, subscribe } = useWebSocket()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  // Fetch data with SWR
  const { data: markets = [], error: marketsError } = useSWR(
    'featured-markets',
    () => marketApi.getMarkets({ limit: 50, tradeable_only: true }).then(res => res.data.markets),
    { refreshInterval: 30000 }
  )

  const { data: news = [], error: newsError } = useSWR(
    'trending-news',
    () => newsApi.getTrendingNews({ limit: 8 }).then(res => res.data.articles),
    { refreshInterval: 60000 }
  )

  // Calculate dashboard stats
  const stats: DashboardStats = {
    totalMarkets: markets.length,
    activeMarkets: markets.filter((m: Market) => m.active).length,
    totalVolume: markets.reduce((acc: number, m: Market) => acc + (m.spread * 1000), 0),
    avgSpread: markets.length > 0 ? markets.reduce((acc: number, m: Market) => acc + m.spread, 0) / markets.length : 0
  }

  // Helper function to get market price
  const getMarketPrice = (market: Market): number => {
    try {
      const pricesStr = market.outcome_prices || '0.5,0.5';
      
      // Handle both JSON array format "[0.5, 0.5]" and comma-separated "0.5,0.5"
      let prices: number[];
      if (pricesStr.startsWith('[') && pricesStr.endsWith(']')) {
        // JSON array format
        prices = JSON.parse(pricesStr);
      } else {
        // Comma-separated format
        prices = pricesStr.split(',').map(p => parseFloat(p.trim()));
      }
      
      return Array.isArray(prices) && prices.length > 0 && !isNaN(prices[0]) ? prices[0] : 0.5;
    } catch (error) {
      console.warn('Error parsing market price:', error, 'for market:', market);
      return 0.5;
    }
  };

  // Filter markets based on search and category
  const filteredMarkets = markets.filter((market: Market) => {
    const matchesSearch = market.question.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || market.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = ['all', 'politics', 'sports', 'crypto', 'entertainment', 'tech', 'other']

  useEffect(() => {
    if (connected) {
      subscribe('markets')
      subscribe('news')
    }
  }, [connected, subscribe])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              <span className="text-blue-100">Poly</span><span className="text-yellow-300">Master</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              AI-Powered Prediction Market Trading Platform
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50" asChild>
                <Link href="/markets">
                  <Play className="w-5 h-5 mr-2" />
                  Start Trading
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10" asChild>
                <Link href="/ai-coach">
                  <Brain className="w-5 h-5 mr-2" />
                  AI Analysis
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Markets</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalMarkets}</p>
                  </div>
                  <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
                    <Target className="w-6 h-6 text-blue-600 dark:text-blue-300" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Active Markets</p>
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.activeMarkets}</p>
                  </div>
                  <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
                    <Activity className="w-6 h-6 text-green-600 dark:text-green-300" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Volume</p>
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">${formatCompactNumber(stats.totalVolume)}</p>
                  </div>
                  <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
                    <DollarSign className="w-6 h-6 text-purple-600 dark:text-purple-300" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Avg Spread</p>
                    <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{formatPercentage(stats.avgSpread)}</p>
                  </div>
                  <div className="p-3 bg-orange-100 dark:bg-orange-900 rounded-full">
                    <TrendingUp className="w-6 h-6 text-orange-600 dark:text-orange-300" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Markets Section */}
          <div className="lg:col-span-2">
            <Card className="mb-6">
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    Featured Markets
                  </CardTitle>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search markets..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 w-full sm:w-64 text-gray-900 dark:text-white bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600"
                      />
                    </div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-4">
                  {categories.map((cat) => (
                    <Button
                      key={cat}
                      variant={selectedCategory === cat ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCategory(cat)}
                      className="capitalize"
                    >
                      {cat === 'all' ? 'All' : `${getCategoryIcon(cat)} ${cat}`}
                    </Button>
                  ))}
                </div>
              </CardHeader>
              <CardContent>
                <AnimatePresence>
                  <div className="grid grid-cols-1 gap-4">
                    {filteredMarkets.slice(0, 8).map((market: Market, index: number) => (
                      <motion.div
                        key={market.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ delay: index * 0.05 }}
                        className="group"
                      >
                        <Card className="hover:shadow-md transition-all duration-200 border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-500 bg-white dark:bg-gray-800">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge className={getCategoryColor(market.category)}>
                                    {getCategoryIcon(market.category)} {market.category}
                                  </Badge>
                                  <Badge 
                                    variant="outline" 
                                    className={getMarketStatusColor(market.active, market.funded)}
                                  >
                                    {getMarketStatusText(market.active, market.funded)}
                                  </Badge>
                                </div>
                                <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                  {truncateText(market.question, 120)}
                                </h3>
                                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                                  <span className="flex items-center gap-1">
                                    <Clock className="w-4 h-4" />
                                    Ends {formatRelativeTime(market.end)}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Users className="w-4 h-4" />
                                    Spread: {formatPercentage(market.spread)}
                                  </span>
                                </div>
                              </div>
                              <div className="flex flex-col items-end gap-2 ml-4">
                                <div className="text-right">
                                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                                    {formatPercentage(getMarketPrice(market))}
                                  </div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400">Current Price</div>
                                </div>
                                <Button size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity" asChild>
                                  <Link href="/markets">
                                    Trade <ChevronRight className="w-4 h-4 ml-1" />
                                  </Link>
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </div>
                </AnimatePresence>
                
                {filteredMarkets.length === 0 && (
                  <div className="text-center py-12">
                    <AlertCircle className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">No markets found matching your criteria</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* AI Coach Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-500" />
                  AI Trading Coach
                </CardTitle>
                <CardDescription>
                  Get personalized insights and recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                      <div className="text-sm">
                        <p className="font-medium text-purple-900">Market Alert</p>
                        <p className="text-purple-700">High volatility detected in crypto markets</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div className="text-sm">
                        <p className="font-medium text-blue-900">Trading Tip</p>
                        <p className="text-blue-700">Consider the upcoming election impact on political markets</p>
                      </div>
                    </div>
                  </div>
                </div>
                <Button className="w-full mt-4" variant="outline" asChild>
                  <Link href="/ai-coach">
                    <Brain className="w-4 h-4 mr-2" />
                    Chat with AI Coach
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Trending News */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <NewspaperIcon className="w-5 h-5 text-blue-500" />
                  Trending News
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {news.slice(0, 4).map((article: NewsArticle, index: number) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="group cursor-pointer"
                    >
                      <div className="flex gap-3">
                        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                          {article.urlToImage ? (
                            <img 
                              src={article.urlToImage} 
                              alt=""
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                            />
                          ) : (
                            <div className="w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                              <NewspaperIcon className="w-6 h-6 text-gray-400" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            {truncateText(article.title || '', 80)}
                          </h4>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {formatRelativeTime(article.publishedAt || '')}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
                <Button className="w-full mt-4" variant="outline" asChild>
                  <Link href="/news">
                    View All News
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button className="w-full justify-start" variant="ghost" asChild>
                    <Link href="/portfolio">
                      <TrendingUp className="w-4 h-4 mr-2" />
                      View Portfolio
                    </Link>
                  </Button>
                  <Button className="w-full justify-start" variant="ghost" asChild>
                    <Link href="/portfolio">
                      <Activity className="w-4 h-4 mr-2" />
                      Trading History
                    </Link>
                  </Button>
                  <Button className="w-full justify-start" variant="ghost" asChild>
                    <Link href="/ai-coach">
                      <Target className="w-4 h-4 mr-2" />
                      Market Analysis
                    </Link>
                  </Button>
                  <Button className="w-full justify-start" variant="ghost" asChild>
                    <Link href="/news">
                      <Zap className="w-4 h-4 mr-2" />
                      Live Updates
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}