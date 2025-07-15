'use client'

import { AutonomousBot } from '@/components/features/trading/AutonomousBot'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { motion } from 'framer-motion'
import { 
  Bot, 
  Brain, 
  Target, 
  TrendingUp,
  Zap,
  Shield,
  Activity,
  Database,
  Search,
  BarChart3
} from 'lucide-react'

export default function TradingBotPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
                <Bot className="w-10 h-10 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              AI Trading Analysis Bot
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Advanced market analysis powered by the original trader.py algorithm with AI-driven insights and opportunity detection (Demo Mode)
            </p>
          </motion.div>
        </div>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-6 h-6 text-purple-500" />
                How the AI Trading Bot Works
              </CardTitle>
              <CardDescription>
                A sophisticated 7-step analysis pipeline from the original PolyAgent
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  {
                    step: 1,
                    title: "Event Discovery",
                    description: "Scans all Polymarket events and identifies high-volume, featured markets",
                    icon: Search,
                    color: "blue"
                  },
                  {
                    step: 2,
                    title: "RAG Filtering",
                    description: "Uses Retrieval-Augmented Generation to filter events by category and quality",
                    icon: Database,
                    color: "green"
                  },
                  {
                    step: 3,
                    title: "Market Mapping",
                    description: "Maps filtered events to tradeable markets with token IDs and pricing data",
                    icon: Target,
                    color: "purple"
                  },
                  {
                    step: 4,
                    title: "AI Analysis",
                    description: "Runs superforecaster analysis with multi-source information synthesis",
                    icon: Brain,
                    color: "orange"
                  },
                  {
                    step: 5,
                    title: "Edge Detection",
                    description: "Calculates trading edge by comparing AI probability vs market prices",
                    icon: TrendingUp,
                    color: "red"
                  },
                  {
                    step: 6,
                    title: "Risk Assessment",
                    description: "Evaluates confidence levels and position sizing for optimal risk/reward",
                    icon: Shield,
                    color: "yellow"
                  },
                  {
                    step: 7,
                    title: "Trade Execution",
                    description: "Executes trades through Polymarket's CLOB with proper position management",
                    icon: Zap,
                    color: "indigo"
                  }
                ].map((step, index) => {
                  const Icon = step.icon
                  return (
                    <motion.div
                      key={step.step}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      className="relative"
                    >
                      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 h-full">
                        <div className="flex items-center gap-3 mb-3">
                          <div className={`w-8 h-8 bg-${step.color}-100 dark:bg-${step.color}-900/20 rounded-full flex items-center justify-center`}>
                            <Icon className={`w-4 h-4 text-${step.color}-600`} />
                          </div>
                          <Badge variant="outline" className="text-xs">
                            Step {step.step}
                          </Badge>
                        </div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                          {step.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {step.description}
                        </p>
                      </div>
                      
                      {index < 6 && (
                        <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gray-300 dark:bg-gray-600 z-10" />
                      )}
                    </motion.div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Trading Bot Component */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <AutonomousBot />
        </motion.div>

        {/* Key Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-6 h-6 text-green-500" />
                Advanced Trading Features
              </CardTitle>
              <CardDescription>
                Professional-grade prediction market trading capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  {
                    title: "Volume-Based Filtering",
                    description: "Only analyzes markets with >$10k volume or featured status for maximum liquidity",
                    icon: "💰"
                  },
                  {
                    title: "Multi-Source Analysis",
                    description: "Combines market data, news sources, and historical patterns for informed decisions",
                    icon: "📊"
                  },
                  {
                    title: "Edge-Driven Trading",
                    description: "Only trades when AI identifies significant pricing inefficiencies vs true probability",
                    icon: "🎯"
                  },
                  {
                    title: "Risk Management",
                    description: "Built-in position sizing, confidence thresholds, and DRY RUN safety mode",
                    icon: "🛡️"
                  },
                  {
                    title: "Real-Time Execution",
                    description: "Direct integration with Polymarket's CLOB for immediate trade execution",
                    icon: "⚡"
                  },
                  {
                    title: "Transparent Reasoning",
                    description: "Full visibility into AI decision-making process and market analysis",
                    icon: "🔍"
                  }
                ].map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    className="p-4 bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                  >
                    <div className="text-2xl mb-3">{feature.icon}</div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Safety Notice */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8"
        >
          <Card className="border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <Shield className="w-6 h-6 text-yellow-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                    Safety & Risk Disclosure
                  </h3>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">
                    This trading bot is for educational and research purposes. Always start with DRY RUN mode to understand the system's behavior before risking real funds.
                  </p>
                  <ul className="text-xs text-yellow-600 dark:text-yellow-400 space-y-1">
                    <li>• Prediction markets involve financial risk and potential loss of capital</li>
                    <li>• AI predictions are not guaranteed and may be incorrect</li>
                    <li>• Always review trades carefully before switching to LIVE mode</li>
                    <li>• Start with small position sizes to test the system</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}