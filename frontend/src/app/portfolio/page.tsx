'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { tradingApi, type Portfolio } from '@/lib/api'
import { formatPrice, formatPercentage, formatRelativeTime, formatCompactNumber } from '@/lib/utils'
import { useWebSocket } from '../providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Wallet,
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart3,
  Activity,
  Clock,
  RefreshCw,
  Download,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  AlertCircle,
  Plus,
  Minus
} from 'lucide-react'
import { PortfolioChart } from '@/components/ui/price-chart'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface Position {
  id: string
  market_question: string
  market_id: string
  side: 'YES' | 'NO'
  shares: number
  avg_cost: number
  current_price: number
  unrealized_pnl: number
  total_value: number
  created_at: string
}

interface TradeHistory {
  id: string
  market_question: string
  side: 'BUY' | 'SELL'
  outcome: 'YES' | 'NO'
  shares: number
  price: number
  total_cost: number
  timestamp: string
  status: 'COMPLETED' | 'PENDING' | 'CANCELLED'
}

export default function PortfolioPage() {
  const { connected } = useWebSocket()
  const [activeTab, setActiveTab] = useState<'overview' | 'positions' | 'history'>('overview')
  
  // Fetch portfolio data
  const { data: portfolio, error: portfolioError, mutate: mutatePortfolio } = useSWR(
    'portfolio',
    () => tradingApi.getPortfolio().then(res => res.data),
    { refreshInterval: 30000 }
  )

  const { data: tradeHistory = [], mutate: mutateHistory } = useSWR(
    'trade-history',
    () => tradingApi.getTradeHistory({ limit: 50 }).then(res => res.data.trades),
    { refreshInterval: 60000 }
  )

  // Mock data for demonstration
  const mockPositions: Position[] = [
    {
      id: '1',
      market_question: 'Will Bitcoin reach $100,000 by end of 2024?',
      market_id: '1',
      side: 'YES',
      shares: 150,
      avg_cost: 0.65,
      current_price: 0.72,
      unrealized_pnl: 10.5,
      total_value: 108,
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      market_question: 'Will Tesla stock price exceed $300 in Q1 2024?',
      market_id: '2',
      side: 'NO',
      shares: 200,
      avg_cost: 0.45,
      current_price: 0.38,
      unrealized_pnl: -14,
      total_value: 76,
      created_at: '2024-01-10T14:20:00Z'
    }
  ]

  const mockHistory: TradeHistory[] = [
    {
      id: '1',
      market_question: 'Will Bitcoin reach $100,000 by end of 2024?',
      side: 'BUY',
      outcome: 'YES',
      shares: 100,
      price: 0.65,
      total_cost: 65,
      timestamp: '2024-01-15T10:30:00Z',
      status: 'COMPLETED'
    },
    {
      id: '2',
      market_question: 'Will Tesla stock price exceed $300 in Q1 2024?',
      side: 'BUY',
      outcome: 'NO',
      shares: 200,
      price: 0.45,
      total_cost: 90,
      timestamp: '2024-01-10T14:20:00Z',
      status: 'COMPLETED'
    }
  ]

  const refreshData = () => {
    mutatePortfolio()
    mutateHistory()
    toast.success('Portfolio data refreshed!')
  }
  
  const runAutonomousTrading = async (dryRun: boolean = true) => {
    try {
      const response = await tradingApi.runAutonomousTrading(dryRun)
      if (response.data.success) {
        toast.success(dryRun ? 'AI Trading Analysis Complete!' : 'Trade Executed Successfully!')
        if (response.data.trade_decision) {
          // Show trading decision details
          toast(
            `AI Decision: ${response.data.trade_decision.action} at $${response.data.trade_decision.target_price}`,
            { duration: 5000 }
          )
        }
      } else {
        toast.error(response.data.message || 'No trading opportunities found')
      }
      // Refresh portfolio data after trading
      refreshData()
    } catch (error) {
      console.error('Error running autonomous trading:', error)
      toast.error('Failed to run autonomous trading')
    }
  }

  const totalPortfolioValue = mockPositions.reduce((acc, pos) => acc + pos.total_value, 0)
  const totalUnrealizedPnL = mockPositions.reduce((acc, pos) => acc + pos.unrealized_pnl, 0)
  const portfolioReturn = totalUnrealizedPnL / (totalPortfolioValue - totalUnrealizedPnL) * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
                  <Wallet className="w-6 h-6 text-white" />
                </div>
                Portfolio
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Track your positions, performance, and trading history
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={refreshData} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button 
                onClick={() => runAutonomousTrading(true)} 
                variant="default" 
                size="sm"
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
              >
                <Activity className="w-4 h-4 mr-2" />
                AI Trading (DRY RUN)
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>

        {/* Portfolio Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Value</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      ${formatCompactNumber(totalPortfolioValue)}
                    </p>
                  </div>
                  <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-full">
                    <DollarSign className="w-6 h-6 text-green-600" />
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
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Unrealized P&L</p>
                    <p className={`text-2xl font-bold ${totalUnrealizedPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {totalUnrealizedPnL >= 0 ? '+' : ''}${totalUnrealizedPnL.toFixed(2)}
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${totalUnrealizedPnL >= 0 ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'}`}>
                    {totalUnrealizedPnL >= 0 ? (
                      <TrendingUp className="w-6 h-6 text-green-600" />
                    ) : (
                      <TrendingDown className="w-6 h-6 text-red-600" />
                    )}
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
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Return</p>
                    <p className={`text-2xl font-bold ${portfolioReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {portfolioReturn >= 0 ? '+' : ''}{portfolioReturn.toFixed(2)}%
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-full">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
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
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Positions</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {mockPositions.length}
                    </p>
                  </div>
                  <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-full">
                    <Target className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: PieChart },
                { id: 'positions', label: 'Positions', icon: Target },
                { id: 'history', label: 'Trade History', icon: Activity }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Portfolio Allocation */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-blue-500" />
                      Portfolio Allocation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg flex items-center justify-center">
                      <div className="w-full max-w-sm">
                        {/* Simple pie chart representation */}
                        <svg viewBox="0 0 200 200" className="w-full h-48">
                          <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" strokeWidth="20"/>
                          <circle 
                            cx="100" 
                            cy="100" 
                            r="80" 
                            fill="none" 
                            stroke="#3b82f6" 
                            strokeWidth="20"
                            strokeDasharray={`${(totalPortfolioValue / (totalPortfolioValue + 500)) * 502} 502`}
                            strokeDashoffset="125.5"
                            transform="rotate(-90 100 100)"
                          />
                          <text x="100" y="100" textAnchor="middle" dy="0.3em" className="text-lg font-bold fill-gray-900 dark:fill-white">
                            {((totalPortfolioValue / (totalPortfolioValue + 500)) * 100).toFixed(0)}%
                          </text>
                          <text x="100" y="120" textAnchor="middle" className="text-xs fill-gray-500">
                            Allocation
                          </text>
                        </svg>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Performance Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-green-500" />
                      Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <PortfolioChart height={200} width={350} timeRange="30d" />
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-purple-500" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockHistory.slice(0, 3).map((trade, index) => (
                      <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-full ${
                            trade.side === 'BUY' ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'
                          }`}>
                            {trade.side === 'BUY' ? (
                              <Plus className="w-4 h-4 text-green-600" />
                            ) : (
                              <Minus className="w-4 h-4 text-red-600" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium text-sm">{trade.side} {trade.outcome}</p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-1">
                              {trade.market_question}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-sm">${trade.total_cost}</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {formatRelativeTime(trade.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab === 'positions' && (
            <motion.div
              key="positions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-500" />
                    Active Positions
                  </CardTitle>
                  <CardDescription>
                    Your current market positions and their performance
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockPositions.map((position, index) => (
                      <motion.div
                        key={position.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                              {position.market_question}
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <p className="text-gray-600 dark:text-gray-400">Position</p>
                                <div className="flex items-center gap-1">
                                  <Badge variant={position.side === 'YES' ? 'default' : 'secondary'}>
                                    {position.side}
                                  </Badge>
                                  <span className="font-medium">{position.shares} shares</span>
                                </div>
                              </div>
                              <div>
                                <p className="text-gray-600 dark:text-gray-400">Avg Cost</p>
                                <p className="font-medium">{formatPercentage(position.avg_cost)}</p>
                              </div>
                              <div>
                                <p className="text-gray-600 dark:text-gray-400">Current Price</p>
                                <p className="font-medium">{formatPercentage(position.current_price)}</p>
                              </div>
                              <div>
                                <p className="text-gray-600 dark:text-gray-400">P&L</p>
                                <p className={`font-medium ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                                </p>
                              </div>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <p className="text-sm text-gray-600 dark:text-gray-400">Total Value</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              ${position.total_value}
                            </p>
                            <Button size="sm" variant="outline" className="mt-2">
                              <Eye className="w-3 h-3 mr-1" />
                              View Market
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  
                  {mockPositions.length === 0 && (
                    <div className="text-center py-12">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 dark:text-gray-400">No active positions</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-purple-500" />
                    Trade History
                  </CardTitle>
                  <CardDescription>
                    Complete history of your trading activity
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockHistory.map((trade, index) => (
                      <motion.div
                        key={trade.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-full ${
                            trade.side === 'BUY' ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'
                          }`}>
                            {trade.side === 'BUY' ? (
                              <ArrowUpRight className="w-4 h-4 text-green-600" />
                            ) : (
                              <ArrowDownRight className="w-4 h-4 text-red-600" />
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`font-medium ${
                                trade.side === 'BUY' ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {trade.side}
                              </span>
                              <Badge variant={trade.outcome === 'YES' ? 'default' : 'secondary'}>
                                {trade.outcome}
                              </Badge>
                              <span className="text-sm text-gray-600 dark:text-gray-400">
                                {trade.shares} shares @ {formatPercentage(trade.price)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                              {trade.market_question}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${trade.total_cost}</p>
                          <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                            <Clock className="w-3 h-3" />
                            {formatRelativeTime(trade.timestamp)}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  
                  {mockHistory.length === 0 && (
                    <div className="text-center py-12">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 dark:text-gray-400">No trading history available</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}