import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data.news.client import News
from agents.data.news.search import MarketSearch
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.news_client = News()
        self.search_client = MarketSearch()
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    async def get_market_news(self, keywords: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news articles related to market keywords"""
        try:
            cache_key = f"market_news_{keywords}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            loop = asyncio.get_event_loop()
            articles = await loop.run_in_executor(
                None,
                self.news_client.get_articles_for_cli_keywords,
                keywords
            )
            
            # Convert to dict format
            articles_data = []
            for article in articles[:limit]:
                article_dict = {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "urlToImage": article.urlToImage,
                    "publishedAt": article.publishedAt,
                    "content": article.content,
                    "source": {
                        "id": article.source.id if article.source else None,
                        "name": article.source.name if article.source else None
                    } if article.source else None,
                    "author": article.author,
                    "relevance_score": self._calculate_relevance(article.title, keywords)
                }
                articles_data.append(article_dict)
                
            # Sort by relevance and recency
            articles_data.sort(key=lambda x: (x["relevance_score"], x["publishedAt"]), reverse=True)
            
            self._set_cache(cache_key, articles_data)
            return articles_data
            
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            raise
            
    async def get_category_news(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news articles for a specific category"""
        try:
            cache_key = f"category_news_{category}_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            # Map categories to news categories
            category_map = {
                "politics": "politics",
                "sports": "sports",
                "crypto": "technology",
                "entertainment": "entertainment",
                "tech": "technology"
            }
            
            news_category = category_map.get(category, "general")
            
            loop = asyncio.get_event_loop()
            articles = await loop.run_in_executor(
                None,
                self.news_client.get_articles_for_category,
                news_category
            )
            
            articles_data = []
            for article in articles[:limit]:
                article_dict = {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "urlToImage": article.urlToImage,
                    "publishedAt": article.publishedAt,
                    "content": article.content,
                    "source": {
                        "id": article.source.id if article.source else None,
                        "name": article.source.name if article.source else None
                    } if article.source else None,
                    "author": article.author,
                    "category": category
                }
                articles_data.append(article_dict)
                
            self._set_cache(cache_key, articles_data)
            return articles_data
            
        except Exception as e:
            logger.error(f"Error getting category news: {e}")
            raise
            
    async def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for news using Tavily"""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.search_client.search,
                query
            )
            
            # Convert search results to article format
            articles_data = []
            for result in results[:limit]:
                article_dict = {
                    "title": result.get("title", ""),
                    "description": result.get("content", ""),
                    "url": result.get("url", ""),
                    "urlToImage": None,
                    "publishedAt": datetime.now().isoformat(),
                    "content": result.get("content", ""),
                    "source": {
                        "id": None,
                        "name": "Tavily Search"
                    },
                    "author": None,
                    "search_score": result.get("score", 0)
                }
                articles_data.append(article_dict)
                
            return articles_data
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            raise
            
    async def get_trending_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending news across all categories"""
        try:
            cache_key = f"trending_news_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            # Get news from multiple categories
            categories = ["politics", "sports", "crypto", "entertainment", "tech"]
            all_articles = []
            
            for category in categories:
                try:
                    articles = await self.get_category_news(category, limit=5)
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error getting {category} news: {e}")
                    continue
                    
            # Sort by publication date
            all_articles.sort(key=lambda x: x["publishedAt"], reverse=True)
            
            trending_articles = all_articles[:limit]
            self._set_cache(cache_key, trending_articles)
            return trending_articles
            
        except Exception as e:
            logger.error(f"Error getting trending news: {e}")
            raise
            
    async def get_news_sentiment(self, article_text: str) -> Dict[str, Any]:
        """Get sentiment analysis for news article"""
        try:
            # TODO: Implement sentiment analysis
            # For now, return placeholder
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.5
            }
            
        except Exception as e:
            logger.error(f"Error getting news sentiment: {e}")
            raise
            
    def _calculate_relevance(self, title: str, keywords: str) -> float:
        """Calculate relevance score for article"""
        try:
            if not title or not keywords:
                return 0.0
                
            title_lower = title.lower()
            keywords_lower = keywords.lower().split()
            
            score = 0.0
            for keyword in keywords_lower:
                if keyword in title_lower:
                    score += 1.0
                    
            return score / len(keywords_lower) if keywords_lower else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0
            
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self.cache:
            return False
        return (datetime.now() - self.cache[key]["timestamp"]).seconds < self.cache_timeout
        
    def _set_cache(self, key: str, data: Any):
        """Set cache entry"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }