from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from services.news_service import NewsService
from api.v1.models.requests.base import GetNewsRequest, SearchNewsRequest, MarketCategory
from api.v1.models.responses.base import NewsResponse, NewsArticleResponse, ErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Import dependency injection functions
from core.dependencies import get_news_service, get_polymarket_service

@router.get("/", response_model=NewsResponse)
async def get_news(
    keywords: Optional[str] = Query(default=None, description="Search keywords"),
    category: Optional[MarketCategory] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    news_service: NewsService = Depends(get_news_service)
):
    """Get news articles with optional filtering"""
    try:
        if keywords:
            # Search by keywords
            articles_data = await news_service.get_market_news(keywords, limit=limit)
            query = keywords
        elif category:
            # Search by category
            articles_data = await news_service.get_category_news(category.value, limit=limit)
            query = None
        else:
            # Get trending news
            articles_data = await news_service.get_trending_news(limit=limit)
            query = None
        
        articles = [NewsArticleResponse(**article) for article in articles_data]
        
        return NewsResponse(
            articles=articles,
            total=len(articles),
            query=query,
            category=category.value if category else None
        )
        
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=NewsResponse)
async def search_news(
    search_request: SearchNewsRequest,
    news_service: NewsService = Depends(get_news_service)
):
    """Search news using Tavily"""
    try:
        articles_data = await news_service.search_news(
            search_request.query, 
            limit=search_request.limit
        )
        
        articles = [NewsArticleResponse(**article) for article in articles_data]
        
        return NewsResponse(
            articles=articles,
            total=len(articles),
            query=search_request.query
        )
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending", response_model=NewsResponse)
async def get_trending_news(
    limit: int = Query(default=20, ge=1, le=50),
    news_service: NewsService = Depends(get_news_service)
):
    """Get trending news across all categories"""
    try:
        articles_data = await news_service.get_trending_news(limit=limit)
        articles = [NewsArticleResponse(**article) for article in articles_data]
        
        return NewsResponse(
            articles=articles,
            total=len(articles),
            query="trending"
        )
        
    except Exception as e:
        logger.error(f"Error getting trending news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/{category}", response_model=NewsResponse)
async def get_category_news(
    category: MarketCategory,
    limit: int = Query(default=10, ge=1, le=50),
    news_service: NewsService = Depends(get_news_service)
):
    """Get news for a specific category"""
    try:
        articles_data = await news_service.get_category_news(category.value, limit=limit)
        articles = [NewsArticleResponse(**article) for article in articles_data]
        
        return NewsResponse(
            articles=articles,
            total=len(articles),
            category=category.value
        )
        
    except Exception as e:
        logger.error(f"Error getting category news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/{market_id}")
async def get_market_related_news(
    market_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    news_service: NewsService = Depends(get_news_service)
):
    """Get news related to a specific market"""
    try:
        # Get market data to extract keywords
        polymarket_service = get_polymarket_service()
        market_data = await polymarket_service.get_market_by_id(market_id)
        
        # Use market question as keywords
        keywords = market_data["question"]
        
        articles_data = await news_service.get_market_news(keywords, limit=limit)
        articles = [NewsArticleResponse(**article) for article in articles_data]
        
        return {
            "market_id": market_id,
            "market_question": keywords,
            "articles": articles,
            "total": len(articles)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting market news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment")
async def analyze_sentiment(
    text: str,
    news_service: NewsService = Depends(get_news_service)
):
    """Analyze sentiment of news text"""
    try:
        sentiment = await news_service.get_news_sentiment(text)
        return sentiment
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))