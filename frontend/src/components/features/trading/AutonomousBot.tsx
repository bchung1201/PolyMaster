'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { tradingApi } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Bot, 
  Play, 
  Pause, 
  Activity, 
  Brain, 
  Target, 
  TrendingUp,
  AlertCircle,
  Check,
  Clock,
  DollarSign,
  Eye,
  Settings,
  Zap,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'

interface TradingDecision {
  market_question: string
  action: string
  position: string
  target_price: number
  edge: number
  confidence: number
  reasoning: string
  analysis: string
}

interface TradingResult {
  success: boolean
  trade_decision?: TradingDecision
  message: string
  dry_run: boolean
  timestamp: string
}

export function AutonomousBot() {
  const [isRunning, setIsRunning] = useState(false)
  const [dryRunMode, setDryRunMode] = useState(true) // Always demo mode for this version
  const [lastResult, setLastResult] = useState<TradingResult | null>(null)
  const [analysisHistory, setAnalysisHistory] = useState<TradingResult[]>([])

  const runTradingCycle = async () => {
    setIsRunning(true)
    try {
      // Always run in dry_run mode for demo (no actual trades)
      const response = await tradingApi.runAutonomousTrading(true)
      const result = response.data as TradingResult
      
      setLastResult(result)
      setAnalysisHistory(prev => [result, ...prev.slice(0, 4)]) // Keep last 5 results
      
      if (result.success) {
        toast.success('🤖 Trading Bot Analysis Complete!', { duration: 3000 })
        
        if (result.trade_decision) {
          toast(
            `Recommendation: ${result.trade_decision.action} at $${result.trade_decision.target_price}`,
            { 
              duration: 5000,
              icon: '🎯'
            }
          )
        }
      } else {
        toast.error(result.message || 'No opportunities found')
      }
    } catch (error) {
      console.error('Error running autonomous trading:', error)
      toast.error('Failed to run trading bot analysis')
    } finally {
      setIsRunning(false)
    }
  }

  // Demo mode - no actual trading, only analysis
  const isDemoMode = true

  return (
    <div className="space-y-6">
      {/* Main Control Panel */}
      <Card className="border-2 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Bot className="w-7 h-7 text-white" />
              </div>
              <div>
                <CardTitle className="flex items-center gap-2">
                  AI Trading Analysis Bot
                  <Badge variant="secondary">
                    DEMO MODE
                  </Badge>
                </CardTitle>
                <CardDescription>
                  AI-powered market analysis using the original trader.py algorithm (no actual trades)
                </CardDescription>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button
                onClick={runTradingCycle}
                disabled={isRunning}
                size="lg"
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
              >
                {isRunning ? (
                  <>
                    <motion.div 
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Brain className="w-5 h-5 mr-2" />
                    </motion.div>
                    Analyzing Markets...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Run Trading Analysis
                  </>
                )}
              </Button>
              
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-3 py-2 rounded-lg">
                <Eye className="w-4 h-4" />
                Demo Mode - Analysis Only
              </div>
            </div>
          </div>
        </CardHeader>

        {lastResult && (
          <CardContent>
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {/* Trading Decision */}
                {lastResult.trade_decision ? (
                  <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                          <Target className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-green-800 dark:text-green-200">
                            AI Trading Decision
                          </h3>
                          <p className="text-sm text-green-600 dark:text-green-400">
                            {new Date(lastResult.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        {lastResult.trade_decision.action}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Target Price</p>
                        <p className="font-semibold">${lastResult.trade_decision.target_price}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Edge</p>
                        <p className="font-semibold text-blue-600">{(lastResult.trade_decision.edge * 100).toFixed(2)}%</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Confidence</p>
                        <p className="font-semibold text-purple-600">{(lastResult.trade_decision.confidence * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm">Market Question:</h4>
                      <p className="text-sm bg-white dark:bg-gray-800 p-2 rounded">
                        {lastResult.trade_decision.market_question}
                      </p>
                      
                      <h4 className="font-medium text-sm">AI Reasoning:</h4>
                      <p className="text-sm bg-white dark:bg-gray-800 p-2 rounded">
                        {lastResult.trade_decision.reasoning}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600" />
                      <span className="font-medium text-yellow-800 dark:text-yellow-200">
                        {lastResult.message}
                      </span>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </CardContent>
        )}
      </Card>

      {/* Analysis History */}
      {analysisHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              Recent Analysis History
            </CardTitle>
            <CardDescription>
              Last {analysisHistory.length} trading bot executions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysisHistory.map((result, index) => (
                <motion.div
                  key={`${result.timestamp}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      result.success ? 'bg-green-500' : 'bg-yellow-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium">
                        {result.trade_decision ? 
                          `${result.trade_decision.action} - ${result.trade_decision.market_question.slice(0, 50)}...` :
                          result.message
                        }
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {new Date(result.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {result.trade_decision && (
                      <>
                        <Badge variant="outline" className="text-xs">
                          Edge: {(result.trade_decision.edge * 100).toFixed(1)}%
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          ${result.trade_decision.target_price}
                        </Badge>
                      </>
                    )}
                    <Badge variant={result.dry_run ? "secondary" : "destructive"} className="text-xs">
                      {result.dry_run ? "DRY" : "LIVE"}
                    </Badge>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bot Features Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Trading Bot Features
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">High-volume market filtering</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">RAG-powered event analysis</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">Edge-based trade decisions</span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">Multi-source information synthesis</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">Confidence-scored predictions</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-sm">Safe DRY RUN mode</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}