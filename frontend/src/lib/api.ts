import axios from 'axios'
import { mockMarkets, mockNews } from './mockData'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000, // 30 seconds for general requests
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Market API
export const marketApi = {
  getMarkets: async (params?: {
    limit?: number
    category?: string
    active_only?: boolean
    sort_by?: string
    tradeable_only?: boolean
  }) => {
    try {
      // Add trailing slash to fix 307 redirect issue
      const response = await api.get('/markets/', { params })
      return response
    } catch (error) {
      console.warn('Backend API unavailable, using mock data:', error)
      // Return mock data in the same format as the API
      let filteredMarkets = mockMarkets
      
      if (params?.category && params.category !== 'all') {
        filteredMarkets = filteredMarkets.filter(m => m.category === params.category)
      }
      
      if (params?.active_only) {
        filteredMarkets = filteredMarkets.filter(m => m.active)
      }
      
      if (params?.limit) {
        filteredMarkets = filteredMarkets.slice(0, params.limit)
      }
      
      return {
        data: {
          markets: filteredMarkets,
          total: filteredMarkets.length
        },
        status: 200
      }
    }
  },
  
  getMarket: (id: string) => api.get(`/markets/${id}`),
  
  getMarketOrderbook: (id: string) => api.get(`/markets/${id}/orderbook`),
  
  getMarketPrice: (id: string) => api.get(`/markets/${id}/price`),
  
  getEvents: (params?: {
    limit?: number
    category?: string
    active_only?: boolean
  }) => api.get('/markets/events', { params }),
  
  getWalletBalance: () => api.get('/markets/wallet/balance'),
}

// Trading API
export const tradingApi = {
  getTradingOpportunities: (params?: { limit?: number }) => 
    api.get('/trading/opportunities', { params }),
  
  executeTrade: (data: {
    market_id: string
    side: 'BUY' | 'SELL'
    amount: number
    dry_run?: boolean
  }) => api.post('/trading/execute', data),
  
  validateTrade: (data: {
    market_id: string
    side: 'BUY' | 'SELL'
    amount: number
    dry_run?: boolean
  }) => api.post('/trading/validate', data),
  
  getPortfolio: () => api.get('/trading/portfolio'),
  
  getTradeHistory: (params?: { limit?: number }) => 
    api.get('/trading/history', { params }),
  
  getTradingStrategy: (data: {
    market_id: string
    include_news?: boolean
  }) => api.post('/trading/strategy', data),
  
  getMarketAnalysis: (marketId: string, outcome: string = 'yes') => 
    api.get(`/trading/analysis/${marketId}`, { params: { outcome } }),
  
  runAutonomousTrading: (dryRun: boolean = true) => 
    api.post('/trading/autonomous', {}, { params: { dry_run: dryRun } }),
}

// News API
export const newsApi = {
  getNews: async (params?: {
    keywords?: string
    category?: string
    limit?: number
  }) => {
    try {
      const response = await api.get('/news', { params })
      return response
    } catch (error) {
      console.warn('Backend API unavailable, using mock news data:', error)
      let filteredNews = mockNews
      
      if (params?.category && params.category !== 'all') {
        filteredNews = filteredNews.filter(n => n.category === params.category)
      }
      
      if (params?.limit) {
        filteredNews = filteredNews.slice(0, params.limit)
      }
      
      return {
        data: {
          articles: filteredNews,
          total: filteredNews.length
        },
        status: 200
      }
    }
  },
  
  searchNews: (data: {
    query: string
    limit?: number
  }) => api.post('/news/search', data),
  
  getTrendingNews: async (params?: { limit?: number }) => {
    try {
      const response = await api.get('/news/trending', { params })
      return response
    } catch (error) {
      console.warn('Backend API unavailable, using mock trending news:', error)
      let trendingNews = mockNews.slice(0, params?.limit || 10)
      return {
        data: {
          articles: trendingNews,
          total: trendingNews.length
        },
        status: 200
      }
    }
  },
  
  getCategoryNews: async (category: string, params?: { limit?: number }) => {
    try {
      const response = await api.get(`/news/categories/${category}`, { params })
      return response
    } catch (error) {
      console.warn('Backend API unavailable, using mock category news:', error)
      let categoryNews = mockNews.filter(n => n.category === category)
      if (params?.limit) {
        categoryNews = categoryNews.slice(0, params.limit)
      }
      return {
        data: {
          articles: categoryNews,
          total: categoryNews.length
        },
        status: 200
      }
    }
  },
  
  getMarketNews: (marketId: string, params?: { limit?: number }) => 
    api.get(`/news/market/${marketId}`, { params }),
  
  analyzeSentiment: (text: string) => 
    api.post('/news/sentiment', { text }),
}

// AI API
export const aiApi = {
  analyzeMarket: (data: {
    market_question: string
    outcome?: string
  }) => api.post('/ai/analyze', data),
  
  chatWithAI: (data: {
    message: string
  }) => api.post('/ai/chat', data),
  
  getMarketRecommendations: (params?: {
    category?: string
    limit?: number
  }) => api.get('/ai/recommendations', { params }),
  
  getPolymarketInsights: (query: string) => 
    api.post('/ai/insights', { query }),
  
  createMarketIdea: () => api.post('/ai/market-idea'),
  
  analyzeNewsImpact: (data: {
    market_question: string
    news_articles: any[]
  }) => api.post('/ai/news-impact', data),
  
  getAICoachAnalysis: (marketId: string) => 
    api.get(`/ai/coach/${marketId}`),
  
  // Enhanced CLI-based AI methods from PolyMaster
  getRelevantNews: (keywords: string) => 
    api.get('/ai/news', { params: { keywords } }),
  
  getFilteredMarkets: (params?: { limit?: number, sort_by?: string }) =>
    api.get('/ai/markets/filtered', { params }),
  
  getFilteredEvents: (params?: { limit?: number, sort_by?: string }) =>
    api.get('/ai/events/filtered', { params }),
  
  askSuperforecaster: (data: {
    event_title: string
    market_question: string
    outcome?: string
  }) => api.post('/ai/superforecaster', {}, { params: data }),
  
  getTradingBotAnalysis: () => 
    api.post('/ai/trading-analysis'),
  
  // ===== NEW ENHANCED METHODS USING SPECIFIC PROMPTS =====
  
  getProfessionalMarketAnalysis: (data: {
    market_question: string
    outcome?: string
  }) => api.post('/ai/professional-analysis', data),
  
  getNewsWithSentiment: (keywords: string) => 
    api.get('/ai/news-sentiment', { params: { keywords } }),
  
  calculateMarketEdge: (data: {
    market_question: string
    outcome?: string
  }) => api.post('/ai/edge-calculation', data),
  
  getComprehensiveMarketInsights: (market_question: string) => 
    api.get('/ai/market-insights', { params: { market_question } }),
}

// Health API
export const healthApi = {
  getHealth: () => api.get('/health'),
}

// Types
export interface Market {
  id: number
  question: string
  end: string
  description: string
  active: boolean
  funded: boolean
  rewardsMinSize: number
  rewardsMaxSpread: number
  spread: number
  outcomes: string
  outcome_prices: string
  clob_token_ids: string | null
  category: string
}

export interface NewsArticle {
  title: string | null
  description: string | null
  url: string | null
  urlToImage: string | null
  publishedAt: string | null
  content: string | null
  source: {
    id: string | null
    name: string | null
  } | null
  author: string | null
  category?: string
  relevance_score?: number
}

export interface TradingOpportunity {
  market: Market
  analysis: string
  category: string
  spread: number
  priority: number
}

export interface Portfolio {
  balance: {
    usdc_balance: number
    wallet_address: string
    last_updated: string
  }
  positions: any[]
  total_value: number
  last_updated: string
}

export interface AIAnalysis {
  market_question: string
  outcome: string
  analysis: string
  timestamp: string
  model: string
}