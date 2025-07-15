'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { aiApi, marketApi, type Market } from '@/lib/api'
import { formatRelativeTime, formatPercentage } from '@/lib/utils'
import { useWebSocket } from '../providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain,
  Send,
  Sparkles,
  TrendingUp,
  Target,
  Lightbulb,
  MessageSquare,
  User,
  Bot,
  RefreshCw,
  Download,
  Share2,
  BookmarkPlus,
  AlertCircle
} from 'lucide-react'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  type?: 'text' | 'analysis' | 'recommendation'
  marketData?: Market
}

interface MarketRecommendation {
  market: Market
  analysis: string
  confidence: number
  recommendation: 'BUY' | 'SELL' | 'HOLD'
}

export default function AICoachPage() {
  const { connected } = useWebSocket()
  const [activeTab, setActiveTab] = useState<'chat' | 'markets' | 'events' | 'news'>('chat')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI Trading Coach. I can help you analyze markets, understand trends, and make informed trading decisions. What would you like to explore today?',
      timestamp: new Date(),
      type: 'text'
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [newsKeywords, setNewsKeywords] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Enhanced CLI-based data fetching
  const { data: filteredMarkets = [], mutate: mutateFilteredMarkets } = useSWR(
    'ai-filtered-markets',
    () => aiApi.getFilteredMarkets({ limit: 10, sort_by: 'spread' }).then(res => res.data.markets),
    { refreshInterval: 300000 }
  )
  
  const { data: filteredEvents = [], mutate: mutateFilteredEvents } = useSWR(
    'ai-filtered-events', 
    () => aiApi.getFilteredEvents({ limit: 10 }).then(res => res.data.events),
    { refreshInterval: 300000 }
  )
  
  const [relevantNews, setRelevantNews] = useState<any[]>([])
  const [superforecasterResults, setSuperforecasterResults] = useState<any[]>([])
  
  // Fetch market recommendations
  const { data: recommendations = [], mutate: mutateRecommendations } = useSWR(
    'ai-recommendations',
    () => aiApi.getMarketRecommendations({ limit: 5 }).then(res => res.data.recommendations),
    { refreshInterval: 300000 }
  )

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await aiApi.chatWithAI({ message: inputMessage })
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response || 'I apologize, but I couldn\'t process your request right now.',
        timestamp: new Date(),
        type: 'text'
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting right now. Please try again later.',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to get AI response')
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = async (action: string) => {
    setIsLoading(true)
    
    const actionMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: action,
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, actionMessage])

    try {
      let response
      switch (action) {
        case 'Analyze trending markets':
          response = await aiApi.getMarketRecommendations({ limit: 3 })
          break
        case 'Get trading strategy':
          response = await aiApi.chatWithAI({ message: 'What\'s your recommended trading strategy for today?' })
          break
        case 'Market sentiment analysis':
          response = await aiApi.chatWithAI({ message: 'What\'s the current market sentiment?' })
          break
        case 'Run trading bot analysis':
          response = await aiApi.getTradingBotAnalysis()
          break
        default:
          response = await aiApi.chatWithAI({ message: action })
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response || response.data.analysis || 'Analysis completed.',
        timestamp: new Date(),
        type: action.includes('Analyze') || action.includes('trading bot') ? 'analysis' : 'text'
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      toast.error('Failed to process request')
    } finally {
      setIsLoading(false)
    }
  }

  const exportChat = () => {
    const chatText = messages.map(msg => 
      `[${msg.timestamp.toLocaleTimeString()}] ${msg.role.toUpperCase()}: ${msg.content}`
    ).join('\n\n')
    
    const blob = new Blob([chatText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `polymaster-ai-coach-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }
  
  // Enhanced CLI-based functions
  const searchRelevantNews = async () => {
    if (!newsKeywords.trim()) return
    
    setIsLoading(true)
    try {
      const response = await aiApi.getRelevantNews(newsKeywords)
      setRelevantNews(response.data.articles || [])
      toast.success(`Found ${response.data.count || 0} relevant articles`)
    } catch (error) {
      toast.error('Failed to fetch news')
    } finally {
      setIsLoading(false)
    }
  }
  
  const askSuperforecaster = async (event: any) => {
    setIsLoading(true)
    try {
      const response = await aiApi.askSuperforecaster({
        event_title: event.title || event.question,
        market_question: event.question || event.title,
        outcome: 'yes'
      })
      
      setSuperforecasterResults(prev => [response.data, ...prev.slice(0, 4)]) // Keep last 5
      toast.success('Superforecaster analysis complete!')
    } catch (error) {
      toast.error('Failed to get superforecaster analysis')
    } finally {
      setIsLoading(false)
    }
  }
  
  const refreshAllData = async () => {
    setIsLoading(true)
    try {
      await Promise.all([
        mutateRecommendations(),
        mutateFilteredMarkets(),
        mutateFilteredEvents()
      ])
      toast.success('All data refreshed!')
    } catch (error) {
      toast.error('Failed to refresh data')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                AI Trading Coach
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Get personalized trading insights, market analysis, and autonomous trading bot analysis powered by AI
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={exportChat} variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export Chat
              </Button>
              <Button onClick={() => setMessages(messages.slice(0, 1))} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Clear Chat
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[700px] flex flex-col">
              <CardHeader className="border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-500" />
                    Chat with AI Coach
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
              </CardHeader>
              
              {/* Messages */}
              <CardContent className="flex-1 overflow-y-auto p-6">
                <div className="space-y-4">
                  <AnimatePresence>
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                        )}
                        
                        <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                          <div className={`rounded-lg p-4 ${
                            message.role === 'user' 
                              ? 'bg-blue-500 text-white ml-auto'
                              : message.type === 'analysis'
                              ? 'bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-700'
                              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                          }`}>
                            {message.type === 'analysis' && (
                              <div className="flex items-center gap-2 mb-2">
                                <Sparkles className="w-4 h-4 text-purple-500" />
                                <span className="text-sm font-medium text-purple-700 dark:text-purple-300">
                                  AI Analysis
                                </span>
                              </div>
                            )}
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            {message.marketData && (
                              <div className="mt-3 p-3 bg-white/50 dark:bg-gray-900/50 rounded border">
                                <h4 className="font-medium text-sm mb-1">{message.marketData.question}</h4>
                                <div className="flex gap-4 text-xs text-gray-600 dark:text-gray-400">
                                  <span>Spread: {formatPercentage(message.marketData.spread)}</span>
                                  <span>Ends: {formatRelativeTime(message.marketData.end)}</span>
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-1 px-1">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                        
                        {message.role === 'user' && (
                          <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center flex-shrink-0">
                            <User className="w-4 h-4 text-white" />
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex gap-3 justify-start"
                    >
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <RefreshCw className="w-4 h-4 animate-spin text-gray-500" />
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            AI is thinking...
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </CardContent>
              
              {/* Input */}
              <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask me about markets, trading strategies, or analysis..."
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleSendMessage} 
                    disabled={isLoading || !inputMessage.trim()}
                    size="sm"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
                
                {/* Quick Actions */}
                <div className="flex flex-wrap gap-2 mt-3">
                  {[
                    'Analyze trending markets',
                    'Get trading strategy', 
                    'Market sentiment analysis',
                    'Best opportunities today',
                    'Run trading bot analysis'
                  ].map((action) => (
                    <Button
                      key={action}
                      size="sm"
                      variant="outline"
                      onClick={() => handleQuickAction(action)}
                      disabled={isLoading}
                      className="text-xs"
                    >
                      {action}
                    </Button>
                  ))}
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* AI Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-green-500" />
                  AI Recommendations
                </CardTitle>
                <CardDescription>
                  Top market opportunities identified by AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendations.slice(0, 3).map((rec: any, index: number) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm line-clamp-2">
                          Market Analysis Available
                        </h4>
                        <Badge variant="secondary" className="text-xs">
                          High Priority
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                        AI has identified potential trading opportunities
                      </p>
                      <Button size="sm" variant="outline" className="w-full text-xs">
                        View Analysis
                      </Button>
                    </motion.div>
                  ))}
                </div>
                <Button className="w-full mt-4" variant="outline">
                  View All Recommendations
                </Button>
              </CardContent>
            </Card>

            {/* Quick Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-500" />
                  Quick Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-yellow-600 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-yellow-900 dark:text-yellow-100">Market Trend</p>
                        <p className="text-yellow-700 dark:text-yellow-300">Bullish momentum in tech markets</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-blue-900 dark:text-blue-100">Risk Alert</p>
                        <p className="text-blue-700 dark:text-blue-300">High volatility expected this week</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Sparkles className="w-4 h-4 text-green-600 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-green-900 dark:text-green-100">Opportunity</p>
                        <p className="text-green-700 dark:text-green-300">3 undervalued markets detected</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Chat Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Share2 className="w-5 h-5 text-purple-500" />
                  Chat Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button className="w-full justify-start" variant="ghost" size="sm">
                    <BookmarkPlus className="w-4 h-4 mr-2" />
                    Save Conversation
                  </Button>
                  <Button className="w-full justify-start" variant="ghost" size="sm">
                    <Share2 className="w-4 h-4 mr-2" />
                    Share Analysis
                  </Button>
                  <Button className="w-full justify-start" variant="ghost" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export Report
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