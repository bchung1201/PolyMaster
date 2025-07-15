from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MarketResponse(BaseModel):
    id: int
    question: str
    end: str
    description: str
    active: bool
    funded: bool
    rewardsMinSize: float
    rewardsMaxSpread: float
    spread: float
    outcomes: str
    outcome_prices: str
    clob_token_ids: Optional[str]
    category: str

class EventResponse(BaseModel):
    id: str
    title: str
    description: str
    markets: str
    metadata: Dict[str, Any]

class MarketsResponse(BaseModel):
    markets: List[MarketResponse]
    total: int
    page: int = 1
    limit: int

class EventsResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int = 1
    limit: int

class OrderbookResponse(BaseModel):
    market: str
    asset_id: str
    bids: List[Dict[str, str]]
    asks: List[Dict[str, str]]
    last_updated: str

class WalletBalanceResponse(BaseModel):
    usdc_balance: float
    wallet_address: str
    last_updated: str

class NewsArticleResponse(BaseModel):
    title: Optional[str]
    description: Optional[str]
    url: Optional[str]
    urlToImage: Optional[str]
    publishedAt: Optional[str]
    content: Optional[str]
    source: Optional[Dict[str, Any]]
    author: Optional[str]
    category: Optional[str] = None
    relevance_score: Optional[float] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticleResponse]
    total: int
    query: Optional[str] = None
    category: Optional[str] = None

class TradeExecutionResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]]
    market_id: str
    side: str
    amount: float
    dry_run: bool
    timestamp: str
    error: Optional[str] = None

class TradingOpportunityResponse(BaseModel):
    market: MarketResponse
    analysis: str
    category: str
    spread: float
    priority: float

class TradingOpportunitiesResponse(BaseModel):
    opportunities: List[TradingOpportunityResponse]
    total: int
    timestamp: str

class PositionResponse(BaseModel):
    market_id: str
    market_question: str
    outcome: str
    size: float
    current_price: float
    unrealized_pnl: float
    last_updated: str

class PortfolioResponse(BaseModel):
    balance: WalletBalanceResponse
    positions: List[PositionResponse]
    total_value: float
    last_updated: str

class AIAnalysisResponse(BaseModel):
    market_question: str
    outcome: str
    analysis: str
    timestamp: str
    model: str

class ChatResponse(BaseModel):
    message: str
    response: str
    timestamp: str
    model: str

class MarketRecommendationResponse(BaseModel):
    market_id: str
    question: str
    reasoning: str
    confidence: float
    category: str

class MarketRecommendationsResponse(BaseModel):
    recommendations: List[MarketRecommendationResponse]
    total: int
    timestamp: str

class TradingStrategyResponse(BaseModel):
    market_id: str
    strategy: str
    timestamp: str
    model: str

class NewsImpactResponse(BaseModel):
    market_question: str
    news_impact: str
    articles_analyzed: int
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, bool]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())