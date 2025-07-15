'use client'

import { useMemo } from 'react'
import { formatPercentage } from '@/lib/utils'

interface PriceChartProps {
  data?: number[]
  height?: number
  width?: number
  color?: string
  showCurrentPrice?: boolean
  currentPrice?: number
}

export function PriceChart({ 
  data, 
  height = 60, 
  width = 200, 
  color = "#22c55e", 
  showCurrentPrice = true,
  currentPrice 
}: PriceChartProps) {
  // Generate mock price data if none provided
  const priceData = useMemo(() => {
    if (data && data.length > 0) return data
    
    // Generate realistic price movement data
    const points = 30
    // Explicitly handle NaN - NaN || 0.65 still equals NaN!
    const basePrice = (currentPrice !== null && currentPrice !== undefined && !isNaN(currentPrice)) ? currentPrice : 0.65
    // Adjust volatility based on price range - smaller prices need smaller volatility
    const volatility = Math.max(0.01, basePrice * 0.1)
    const trendAmount = Math.max(0.005, basePrice * 0.03)
    
    return Array.from({ length: points }, (_, i) => {
      const trend = Math.sin(i * 0.2) * trendAmount // Slight trending proportional to price
      const noise = (Math.random() - 0.5) * volatility
      const price = Math.max(0.001, Math.min(0.999, basePrice + trend + noise))
      return price
    })
  }, [data, currentPrice])

  const { path, minPrice, maxPrice } = useMemo(() => {
    if (priceData.length === 0) return { path: '', minPrice: 0, maxPrice: 1 }
    
    const min = Math.min(...priceData)
    const max = Math.max(...priceData)
    const range = max - min || 0.1
    
    const points = priceData.map((price, index) => {
      const x = (index / (priceData.length - 1)) * width
      const y = height - ((price - min) / range) * height
      return `${x},${y}`
    }).join(' ')
    
    return {
      path: `M ${points}`,
      minPrice: min,
      maxPrice: max
    }
  }, [priceData, width, height])

  const isPositive = priceData.length > 1 && priceData[priceData.length - 1] > priceData[0]
  const chartColor = isPositive ? "#22c55e" : "#ef4444"

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {/* Background grid */}
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.1"/>
          </pattern>
        </defs>
        <rect width={width} height={height} fill="url(#grid)" />
        
        {/* Price line */}
        <path
          d={path}
          fill="none"
          stroke={chartColor}
          strokeWidth="2"
          className="drop-shadow-sm"
        />
        
        {/* Area fill */}
        <path
          d={`${path} L ${width},${height} L 0,${height} Z`}
          fill={`url(#gradient-${isPositive ? 'green' : 'red'})`}
          opacity="0.1"
        />
        
        {/* Gradients */}
        <defs>
          <linearGradient id="gradient-green" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="#22c55e" stopOpacity="0"/>
          </linearGradient>
          <linearGradient id="gradient-red" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="#ef4444" stopOpacity="0"/>
          </linearGradient>
        </defs>
        
        {/* Current price dot */}
        {showCurrentPrice && priceData.length > 0 && (
          <circle
            cx={width}
            cy={height - ((priceData[priceData.length - 1] - minPrice) / (maxPrice - minPrice || 0.1)) * height}
            r="3"
            fill={chartColor}
            className="drop-shadow-sm"
          />
        )}
      </svg>
      
      {/* Price labels */}
      <div className="absolute top-0 right-0 text-xs text-gray-500">
        {(maxPrice * 100).toFixed(0)}¢
      </div>
      <div className="absolute bottom-0 right-0 text-xs text-gray-500">
        {(minPrice * 100).toFixed(0)}¢
      </div>
    </div>
  )
}

interface PortfolioChartProps {
  data?: { date: string; value: number }[]
  height?: number
  width?: number
  timeRange?: '24h' | '7d' | '30d' | '1y'
}

export function PortfolioChart({ 
  data, 
  height = 200, 
  width = 400, 
  timeRange = '30d' 
}: PortfolioChartProps) {
  // Generate mock portfolio data if none provided
  const portfolioData = useMemo(() => {
    if (data && data.length > 0) return data
    
    const points = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 365
    const baseValue = 1000
    
    return Array.from({ length: points }, (_, i) => {
      const trend = i * 2 // Slight upward trend
      const noise = (Math.random() - 0.5) * 50
      const value = Math.max(500, baseValue + trend + noise)
      return {
        date: new Date(Date.now() - (points - i) * 24 * 60 * 60 * 1000).toISOString(),
        value
      }
    })
  }, [data, timeRange])

  const { path, minValue, maxValue, totalReturn } = useMemo(() => {
    if (portfolioData.length === 0) return { path: '', minValue: 0, maxValue: 1000, totalReturn: 0 }
    
    const values = portfolioData.map(d => d.value)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const range = max - min || 100
    
    const points = portfolioData.map((item, index) => {
      const x = (index / (portfolioData.length - 1)) * width
      const y = height - ((item.value - min) / range) * height
      return `${x},${y}`
    }).join(' ')
    
    const firstValue = portfolioData[0].value
    const lastValue = portfolioData[portfolioData.length - 1].value
    const returnPct = ((lastValue - firstValue) / firstValue) * 100
    
    return {
      path: `M ${points}`,
      minValue: min,
      maxValue: max,
      totalReturn: returnPct
    }
  }, [portfolioData, width, height])

  const isPositive = totalReturn >= 0
  const chartColor = isPositive ? "#22c55e" : "#ef4444"

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-white">Portfolio Performance</h3>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? '+' : ''}{totalReturn.toFixed(2)}%
          </span>
          <span className="text-xs text-gray-500">{timeRange}</span>
        </div>
      </div>
      
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
        {/* Portfolio line */}
        <path
          d={path}
          fill="none"
          stroke={chartColor}
          strokeWidth="3"
        />
        
        {/* Area fill */}
        <path
          d={`${path} L ${width} ${height} L 0 ${height} Z`}
          fill={chartColor}
          opacity="0.1"
        />
      </svg>
      
      {/* Value labels */}
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        <span>${!isNaN(minValue) ? minValue.toFixed(0) : '1000'}</span>
        <span>${!isNaN(maxValue) ? maxValue.toFixed(0) : '1000'}</span>
      </div>
    </div>
  )
}