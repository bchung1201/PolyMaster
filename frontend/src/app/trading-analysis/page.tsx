'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
// Using native select for simplicity
import { aiApi, marketApi, newsApi, type Market, type NewsArticle } from '@/lib/api'
import { formatRelativeTime, formatPercentage } from '@/lib/utils'
import { useWebSocket } from '../providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain,
  TrendingUp,
  Target,
  Search,
  MessageSquare,
  Bot,
  RefreshCw,
  Download,
  AlertCircle,
  Newspaper,
  Calculator,
  Eye,
  Lightbulb,
  BarChart3,
  Activity,
  Zap
} from 'lucide-react'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface AnalysisResult {
  id: string
  type: 'market_analysis' | 'news_analysis' | 'edge_calculation' | 'superforecast'
  title: string
  content: string
  timestamp: Date
  market?: Market
  confidence?: string
  edge?: number
}

export default function TradingAnalysisPage() {
  const { connected } = useWebSocket()
  const [selectedMarket, setSelectedMarket] = useState<Market | null>(null)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [searchKeywords, setSearchKeywords] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Fetch markets for selection
  const { data: markets = [] } = useSWR(
    'available-markets',
    () => marketApi.getMarkets({ limit: 50, active_only: true }).then(res => res.data.markets),
    { refreshInterval: 60000 }
  )

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [analysisResults])

  const addAnalysisResult = (result: Omit<AnalysisResult, 'id' | 'timestamp'>) => {
    const newResult: AnalysisResult = {
      ...result,
      id: Date.now().toString(),
      timestamp: new Date()
    }
    setAnalysisResults(prev => [...prev, newResult])
  }

  const analyzeMarketPricing = async () => {
    if (!selectedMarket) {
      toast.error('Please select a market first')
      return
    }

    setIsLoading(true)
    try {
      const response = await aiApi.getProfessionalMarketAnalysis({
        market_question: selectedMarket.question,
        outcome: 'yes'
      })

      addAnalysisResult({
        type: 'superforecast',
        title: `Professional Superforecaster Analysis: ${selectedMarket.question}`,
        content: response.data.analysis || 'Analysis not available',
        market: selectedMarket,
        confidence: 'High'
      })

      toast.success('Professional market analysis complete!')
    } catch (error: any) {
      console.error('Market analysis error:', error)
      addAnalysisResult({
        type: 'superforecast',
        title: `Analysis Error: ${selectedMarket.question}`,
        content: `Error occurred while analyzing market: ${error?.response?.data?.detail || error.message || 'Unknown error'}`,
        market: selectedMarket,
        confidence: 'Low'
      })
      toast.error('Analysis completed with errors - check results for details')
    } finally {
      setIsLoading(false)
    }
  }

  const getRelevantNews = async () => {
    // Use default keywords if none provided
    const keywords = searchKeywords.trim() || (selectedMarket ? selectedMarket.question.split(' ').slice(0, 3).join(' ') : 'prediction markets')

    setIsLoading(true)
    try {
      // Use the faster method without sentiment analysis for quick news fetching
      const response = await aiApi.getRelevantNews(keywords)
      
      const newsCount = response.data.articles?.length || 0
      const formattedContent = `Found ${newsCount} relevant articles for "${keywords}":

${response.data.articles?.slice(0, 5).map((article: any, index: number) => 
  `${index + 1}. **${article.title}**
   Source: ${article.source?.name || 'Unknown'}
   Published: ${formatRelativeTime(article.publishedAt)}
   ${article.description || 'No description available'}
   
   URL: ${article.url}
`).join('\n\n') || 'No articles found'}`

      addAnalysisResult({
        type: 'news_analysis',
        title: `Relevant News: "${keywords}"`,
        content: formattedContent
      })

      toast.success(`Found ${newsCount} relevant articles`)
    } catch (error: any) {
      console.error('News sentiment error:', error)
      addAnalysisResult({
        type: 'news_analysis',
        title: `News Error: "${keywords}"`,
        content: `Error occurred while fetching news: ${error?.response?.data?.detail || error.message || 'Unknown error'}. This might be due to API limitations or network issues.`,
      })
      toast.error('News analysis completed with errors - check results for details')
    } finally {
      setIsLoading(false)
    }
  }

  const analyzeMarketSentiment = async () => {
    // Use defaults if not provided
    const keywords = searchKeywords.trim() || (selectedMarket ? selectedMarket.question.split(' ').slice(0, 3).join(' ') : 'prediction markets')
    const market = selectedMarket || { question: 'General prediction market sentiment', id: 0 }

    setIsLoading(true)
    try {
      // Use the sentiment analysis method directly for better analysis
      const sentimentResponse = await aiApi.getNewsWithSentiment(keywords)
      
      const newsCount = sentimentResponse.data.articles?.length || 0
      const formattedContent = `Sentiment analysis for "${keywords}" (related to: ${market.question}):

Found ${newsCount} articles with AI sentiment analysis:

${sentimentResponse.data.articles?.slice(0, 3).map((article: any, index: number) => 
  `${index + 1}. **${article.title}**
   Source: ${article.source || 'Unknown'}
   Published: ${formatRelativeTime(article.published_at)}
   ${article.description || 'No description available'}
   
   **AI Sentiment Analysis:** ${article.sentiment_analysis || 'Analysis not available'}
   
   URL: ${article.url}
`).join('\n\n') || 'No articles found'}`

      addAnalysisResult({
        type: 'news_analysis',
        title: `AI Sentiment Analysis: ${market.question}`,
        content: formattedContent,
        market: selectedMarket || undefined
      })

      toast.success(`Sentiment analysis complete for ${newsCount} articles!`)
    } catch (error: any) {
      console.error('Sentiment analysis error:', error)
      addAnalysisResult({
        type: 'news_analysis',
        title: `Sentiment Analysis Error: ${market.question}`,
        content: `Error occurred while analyzing sentiment: ${error?.response?.data?.detail || error.message || 'Unknown error'}. This might be due to API limitations or network issues.`,
        market: selectedMarket || undefined
      })
      toast.error('Sentiment analysis completed with errors - check results for details')
    } finally {
      setIsLoading(false)
    }
  }

  const calculateEdgeOpportunity = async () => {
    if (!selectedMarket) {
      toast.error('Please select a market first')
      return
    }

    setIsLoading(true)
    try {
      const response = await aiApi.calculateMarketEdge({
        market_question: selectedMarket.question,
        outcome: 'yes'
      })

      const data = response.data
      const edgeContent = `**Professional Edge Calculation for: ${selectedMarket.question}**

**Current Market Price:** ${formatPercentage(data.market_price)}
**AI Estimated Probability:** ${formatPercentage(data.ai_probability)}
**Absolute Edge:** ${formatPercentage(data.absolute_edge)}
**Relative Edge:** ${data.relative_edge.toFixed(2)}%

**Professional Analysis:**
${data.edge_analysis}

**Kelly Criterion Position Size:** ${(data.kelly_size * 100).toFixed(2)}% of bankroll

**Confidence Level:** ${data.confidence}

**Trading Recommendation:** ${data.recommendation}

---
*Analysis powered by professional edge calculation using superforecaster methodology*`

      addAnalysisResult({
        type: 'edge_calculation',
        title: `Professional Edge Analysis: ${selectedMarket.question}`,
        content: edgeContent,
        market: selectedMarket,
        edge: data.absolute_edge,
        confidence: data.confidence
      })

      toast.success('Professional edge calculation complete!')
    } catch (error: any) {
      console.error('Edge calculation error:', error)
      addAnalysisResult({
        type: 'edge_calculation',
        title: `Edge Calculation Error: ${selectedMarket.question}`,
        content: `Error occurred while calculating edge: ${error?.response?.data?.detail || error.message || 'Unknown error'}. This might be due to API limitations or network issues.`,
        market: selectedMarket,
        confidence: 'Low'
      })
      toast.error('Edge calculation completed with errors - check results for details')
    } finally {
      setIsLoading(false)
    }
  }

  const generateMarketInsights = async () => {
    if (!selectedMarket) {
      toast.error('Please select a market first')
      return
    }

    setIsLoading(true)
    try {
      const response = await aiApi.getComprehensiveMarketInsights(selectedMarket.question)

      const data = response.data
      const insightsContent = `**Comprehensive Polymarket Analysis for: ${selectedMarket.question}**

**Markets Analyzed:** ${data.markets_analyzed} active markets
**Events Analyzed:** ${data.events_analyzed} current events

**Professional Polymarket Analyst Insights:**
${data.insights}

---
*Analysis generated using professional Polymarket analyst methodology with live market data*`

      addAnalysisResult({
        type: 'market_analysis',
        title: `Comprehensive Market Insights: ${selectedMarket.question}`,
        content: insightsContent,
        market: selectedMarket
      })

      toast.success('Comprehensive market insights generated!')
    } catch (error: any) {
      console.error('Market insights error:', error)
      addAnalysisResult({
        type: 'market_analysis',
        title: `Market Insights Error: ${selectedMarket?.question || 'Unknown Market'}`,
        content: `Error occurred while generating insights: ${error?.response?.data?.detail || error.message || 'Unknown error'}. This might be due to API limitations or network issues.`,
        market: selectedMarket
      })
      toast.error('Market insights completed with errors - check results for details')
    } finally {
      setIsLoading(false)
    }
  }

  const clearAnalysis = () => {
    setAnalysisResults([])
    toast.success('Analysis cleared')
  }

  const exportAnalysis = () => {
    const exportText = analysisResults.map(result => 
      `[${result.timestamp.toLocaleString()}] ${result.title}\n\n${result.content}\n\n---\n\n`
    ).join('')
    
    const blob = new Blob([exportText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `polymaster-trading-analysis-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Analysis exported!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                AI Trading Analysis
              </h1>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl">
                Professional market analysis using superforecaster methodology, live Polymarket data, news sentiment analysis, and edge calculation with Kelly criterion position sizing
              </p>
              {!connected && (
                <div className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  ⚠️ Some features may require API configuration (NEWSAPI_API_KEY for real news data)
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <Button onClick={exportAnalysis} variant="outline" size="sm" disabled={analysisResults.length === 0}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button onClick={clearAnalysis} variant="outline" size="sm" disabled={analysisResults.length === 0}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Analysis Controls */}
          <div className="lg:col-span-1">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-500" />
                  Market Selection
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Select Market</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onChange={(e) => {
                      const market = markets.find((m: any) => m.id.toString() === e.target.value)
                      setSelectedMarket(market || null)
                    }}
                    value={selectedMarket?.id || ''}
                  >
                    <option value="">Choose a market...</option>
                    {markets.slice(0, 20).map((market: Market) => (
                      <option key={market.id} value={market.id.toString()}>
                        {market.question.slice(0, 60)}...
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Keywords for News</label>
                  <Input
                    placeholder="e.g., election, crypto, sports"
                    value={searchKeywords}
                    onChange={(e) => setSearchKeywords(e.target.value)}
                  />
                </div>

                {selectedMarket && (
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="text-sm font-medium mb-1">Selected Market:</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{selectedMarket.question}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline">Spread: {formatPercentage(selectedMarket.spread)}</Badge>
                      <Badge variant="outline">Ends: {formatRelativeTime(selectedMarket.end)}</Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  Analysis Tools
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  onClick={analyzeMarketPricing}
                  disabled={!selectedMarket || isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  Superforecaster Analysis
                </Button>

                <Button 
                  onClick={getRelevantNews}
                  disabled={!selectedMarket || isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Newspaper className="w-4 h-4 mr-2" />
                  Get Relevant News
                </Button>

                <Button 
                  onClick={analyzeMarketSentiment}
                  disabled={!selectedMarket || isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Activity className="w-4 h-4 mr-2" />
                  Analyze Sentiment
                </Button>

                <Button 
                  onClick={calculateEdgeOpportunity}
                  disabled={!selectedMarket || isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Calculator className="w-4 h-4 mr-2" />
                  Calculate Edge
                </Button>

                <Button 
                  onClick={generateMarketInsights}
                  disabled={!selectedMarket || isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Market Insights
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Analysis Results */}
          <div className="lg:col-span-3">
            <Card className="h-[700px] flex flex-col">
              <CardHeader className="border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-blue-500" />
                    Analysis Results
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 overflow-y-auto p-6">
                {analysisResults.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-center">
                    <div>
                      <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 dark:text-gray-400 mb-2">
                        Professional AI Trading Analysis
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        Use the analysis tools on the left to generate professional trading insights
                      </p>
                      <div className="text-xs text-gray-400 space-y-1 max-w-md">
                        <p>• <strong>Superforecaster Analysis:</strong> Market probability assessment using live data</p>
                        <p>• <strong>Get Relevant News:</strong> Fetches related news with sentiment analysis</p>
                        <p>• <strong>Analyze Sentiment:</strong> Combines news and market data for impact assessment</p>
                        <p>• <strong>Calculate Edge:</strong> Identifies trading opportunities using real market prices</p>
                        <p>• <strong>Market Insights:</strong> Comprehensive analysis using live Polymarket data</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <AnimatePresence>
                      {analysisResults.map((result) => (
                        <motion.div
                          key={result.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800"
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-2">
                              {result.type === 'superforecast' && <Brain className="w-4 h-4 text-purple-500" />}
                              {result.type === 'news_analysis' && <Newspaper className="w-4 h-4 text-blue-500" />}
                              {result.type === 'edge_calculation' && <Calculator className="w-4 h-4 text-green-500" />}
                              {result.type === 'market_analysis' && <Lightbulb className="w-4 h-4 text-yellow-500" />}
                              <h3 className="font-semibold text-gray-900 dark:text-white">
                                {result.title}
                              </h3>
                            </div>
                            <div className="text-xs text-gray-500">
                              {result.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                          
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <div 
                              className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap"
                              dangerouslySetInnerHTML={{
                                __html: result.content
                                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                  .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
                                  .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
                                  .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
                                  .replace(/\n/g, '<br>')
                              }}
                            />
                          </div>

                          {result.edge !== undefined && (
                            <div className="mt-3 flex items-center gap-2">
                              <Badge variant={result.edge > 0 ? "default" : "destructive"}>
                                Edge: {formatPercentage(Math.abs(result.edge))}
                              </Badge>
                              {result.confidence && (
                                <Badge variant="outline">
                                  Confidence: {result.confidence}
                                </Badge>
                              )}
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </CardContent>
              
              {isLoading && (
                <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex items-center gap-2 text-blue-600">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Analyzing...</span>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}