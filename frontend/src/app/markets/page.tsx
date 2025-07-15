'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { marketApi, tradingApi, type Market } from '@/lib/api'
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
import { useWebSocket } from '../providers'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TrendingUp, 
  Activity, 
  Target, 
  Search,
  Filter,
  DollarSign,
  Users,
  Clock,
  AlertCircle,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'
import { PriceChart } from '@/components/ui/price-chart'
import useSWR from 'swr'
import toast from 'react-hot-toast'

interface TradingModalProps {
  market: Market | null
  isOpen: boolean
  onClose: () => void
}

function TradingModal({ market, isOpen, onClose }: TradingModalProps) {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
  const [amount, setAmount] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  if (!market || !isOpen) return null

  const handleTrade = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      toast.error('Please enter a valid amount')
      return
    }

    setIsLoading(true)
    try {
      const response = await tradingApi.executeTrade({
        market_id: market.id.toString(),
        side,
        amount: parseFloat(amount),
        dry_run: true
      })
      toast.success(`${side} order placed successfully!`)
      setAmount('')
      onClose()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Trade execution failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Trade Market</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>×</Button>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Market Question</p>
            <p className="font-medium">{truncateText(market.question, 100)}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant={side === 'BUY' ? 'default' : 'outline'}
              onClick={() => setSide('BUY')}
              className="w-full"
            >
              <ArrowUpRight className="w-4 h-4 mr-2" />
              Buy YES
            </Button>
            <Button
              variant={side === 'SELL' ? 'default' : 'outline'}
              onClick={() => setSide('SELL')}
              className="w-full"
            >
              <ArrowDownRight className="w-4 h-4 mr-2" />
              Sell NO
            </Button>
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Amount (USDC)</label>
            <Input
              type="number"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              min="0"
              step="0.01"
            />
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
            <div className="flex justify-between text-sm">
              <span>Estimated Cost:</span>
              <span className="font-medium">${amount || '0.00'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Market Spread:</span>
              <span>{formatPercentage(market.spread)}</span>
            </div>
          </div>
          
          <Button
            onClick={handleTrade}
            disabled={isLoading || !amount}
            className="w-full"
          >
            {isLoading ? 'Processing...' : `${side} ${amount} USDC`}
          </Button>
        </div>
      </motion.div>
    </div>
  )
}

export default function MarketsPage() {
  const { connected } = useWebSocket()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('volume')
  const [selectedMarket, setSelectedMarket] = useState<Market | null>(null)
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false)
  // Fetch data with SWR
  const { data: markets = [], error: marketsError, mutate } = useSWR(
    'all-markets',
    () => marketApi.getMarkets({ 
      limit: 500, 
      active_only: true,
      sort_by: sortBy 
    }).then(res => res.data.markets),
    { refreshInterval: 30000 }
  )

  // Helper function to get market price
  const getMarketPrice = (market: Market): number => {
    try {
      const pricesStr = market.outcome_prices || '0.5,0.5';
      
      // Handle both JSON array format "[0.5, 0.5]" and comma-separated "0.5,0.5"
      let prices: number[];
      if (pricesStr.startsWith('[') && pricesStr.endsWith(']')) {
        // JSON array format - could contain strings or numbers
        const parsedArray = JSON.parse(pricesStr);
        prices = parsedArray.map((p: any) => typeof p === 'string' ? parseFloat(p) : p);
      } else {
        // Comma-separated format
        prices = pricesStr.split(',').map(p => parseFloat(p.trim()));
      }
      
      if (Array.isArray(prices) && prices.length > 0 && !isNaN(prices[0])) {
        return prices[0];
      } else {
        return 0.5;
      }
    } catch (error) {
      console.warn('Error parsing market price:', error);
      return 0.5;
    }
  };

  // Filter markets based on search and category
  const filteredMarkets = markets.filter((market: Market) => {
    const matchesSearch = market.question.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || market.category === selectedCategory
    return matchesSearch && matchesCategory
  })
  

  const categories = ['all', 'politics', 'sports', 'crypto', 'tech', 'entertainment', 'economy', 'climate', 'health', 'other']

  const handleTradeClick = (market: Market) => {
    setSelectedMarket(market)
    setIsTradeModalOpen(true)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Prediction Markets
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Discover and trade on the most active prediction markets
          </p>
        </div>

        {/* Stats */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {filteredMarkets.length} active markets
              </span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {connected ? 'Live data' : 'Cached data'}
              </span>
            </div>
          </div>
        </div>

        {/* Search */}
        <Card className="mb-4">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search markets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 text-gray-900 dark:text-white bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600"
              />
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
              <div className="flex flex-wrap gap-2 flex-1">
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
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="volume">Sort by Volume</option>
                <option value="spread">Sort by Spread</option>
                <option value="end_date">Sort by End Date</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Markets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {filteredMarkets.map((market: Market) => (
              <motion.div
                key={market.id}
                layout
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ 
                  duration: 0.2,
                  layout: { duration: 0.3 }
                }}
              >
                <Card className="hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-blue-300 h-full">
                  <CardContent className="p-6">
                    <div className="flex flex-col h-full">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex flex-wrap gap-2">
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
                      </div>

                      {/* Question */}
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-3 line-clamp-2 flex-1">
                        {market.question}
                      </h3>

                      {/* Market Info */}
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">Current Price</span>
                          <span className="font-bold text-green-600">
                            {formatPercentage(getMarketPrice(market))}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">Spread</span>
                          <span className="font-medium">{formatPercentage(market.spread)}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">Ends</span>
                          <span className="font-medium">{formatRelativeTime(market.end)}</span>
                        </div>
                      </div>

                      {/* Price Chart */}
                      <div className="mb-4 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <PriceChart 
                          height={60} 
                          width={280} 
                          currentPrice={getMarketPrice(market)}
                          showCurrentPrice={true}
                        />
                      </div>

                      {/* Action Buttons */}
                      <div className="grid grid-cols-2 gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-green-600 border-green-600 hover:bg-green-50"
                          onClick={() => handleTradeClick(market)}
                        >
                          <ArrowUpRight className="w-4 h-4 mr-1" />
                          Buy YES
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 border-red-600 hover:bg-red-50"
                          onClick={() => handleTradeClick(market)}
                        >
                          <ArrowDownRight className="w-4 h-4 mr-1" />
                          Sell NO
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Empty State */}
        {filteredMarkets.length === 0 && (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              No markets found matching your criteria
            </p>
          </div>
        )}
      </div>

      {/* Trading Modal */}
      <AnimatePresence>
        {isTradeModalOpen && (
          <TradingModal
            market={selectedMarket}
            isOpen={isTradeModalOpen}
            onClose={() => setIsTradeModalOpen(false)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}