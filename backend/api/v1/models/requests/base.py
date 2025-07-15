from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class MarketCategory(str, Enum):
    POLITICS = "politics"
    SPORTS = "sports"
    CRYPTO = "crypto"
    ENTERTAINMENT = "entertainment"
    TECH = "tech"
    OTHER = "other"

class GetMarketsRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    category: Optional[MarketCategory] = None
    active_only: bool = Field(default=True)
    sort_by: str = Field(default="spread", description="Sort by: spread, volume, end_date")

class GetEventsRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    category: Optional[MarketCategory] = None
    active_only: bool = Field(default=True)

class ExecuteTradeRequest(BaseModel):
    market_id: str = Field(description="Market ID to trade")
    side: TradeSide = Field(description="Buy or sell")
    amount: float = Field(gt=0, description="Amount to trade in USDC")
    dry_run: bool = Field(default=True, description="Execute as dry run")

class GetNewsRequest(BaseModel):
    keywords: Optional[str] = None
    category: Optional[MarketCategory] = None
    limit: int = Field(default=10, ge=1, le=50)

class SearchNewsRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)

class AIAnalysisRequest(BaseModel):
    market_question: str = Field(min_length=1, max_length=500)
    outcome: str = Field(default="yes", description="Outcome to analyze (yes/no)")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

class TradingStrategyRequest(BaseModel):
    market_id: str = Field(description="Market ID for strategy")
    include_news: bool = Field(default=True, description="Include news analysis")

class NewsImpactRequest(BaseModel):
    market_question: str = Field(min_length=1, max_length=500)
    news_articles: List[Dict[str, Any]] = Field(max_items=10)