from datetime import datetime
import os

from newsapi import NewsApiClient

from agents.models.schemas import Article


class News:
    def __init__(self) -> None:
        self.configs = {
            "language": "en",
            "country": "us",
            "top_headlines": "https://newsapi.org/v2/top-headlines?country=us&apiKey=",
            "base_url": "https://newsapi.org/v2/",
        }

        self.categories = {
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        }

        api_key = os.getenv("NEWSAPI_API_KEY")
        self.api_key_configured = bool(api_key and api_key != "your_news_api_key")
        if not self.api_key_configured:
            print(f"Warning: NEWSAPI_API_KEY not properly configured")
        self.API = NewsApiClient(api_key)

    def get_articles_for_cli_keywords(self, keywords) -> "list[Article]":
        # Check if API key is available
        if not os.getenv("NEWSAPI_API_KEY"):
            print(f"Warning: NEWSAPI_API_KEY not configured, returning empty results")
            return []
            
        try:
            query_words = keywords.split(",")
            all_articles = self.get_articles_for_options(query_words)
            article_objects: list[Article] = []
            for _, articles in all_articles.items():
                for article in articles:
                    article_objects.append(Article(**article))
            return article_objects
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []

    def get_top_articles_for_market(self, market_object: dict) -> "list[Article]":
        return self.API.get_top_headlines(
            language="en", country="usa", q=market_object["description"]
        )

    def get_articles_for_options(
        self,
        market_options: "list[str]",
        date_start: datetime = None,
        date_end: datetime = None,
    ) -> "list[Article]":

        all_articles = {}
        # Default to top articles if no start and end dates are given for search
        if not date_start and not date_end:
            for option in market_options:
                # Use get_everything for query searches since get_top_headlines 
                # doesn't allow both q and country parameters
                response_dict = self.API.get_everything(
                    q=option.strip(),
                    language=self.configs["language"],
                    sort_by="publishedAt",
                    page_size=10  # Reduced from 20 to 10 for faster processing
                )
                articles = response_dict["articles"]
                all_articles[option] = articles
        else:
            for option in market_options:
                response_dict = self.API.get_everything(
                    q=option.strip(),
                    language=self.configs["language"],
                    country=self.configs["country"],
                    from_param=date_start,
                    to=date_end,
                )
                articles = response_dict["articles"]
                all_articles[option] = articles

        return all_articles

    def get_category(self, market_object: dict) -> str:
        news_category = "general"
        market_category = market_object["category"]
        if market_category in self.categories:
            news_category = market_category
        return news_category

    def get_articles_for_category(self, category: str) -> "list[Article]":
        """Get articles for a specific news category"""
        # Ensure the category is valid, default to 'general' if not
        news_category = category if category in self.categories else "general"
        
        try:
            response_dict = self.API.get_top_headlines(
                category=news_category,
                language=self.configs["language"],
                country=self.configs["country"],
            )
            
            articles = response_dict.get("articles", [])
            article_objects: list[Article] = []
            
            for article in articles:
                try:
                    article_objects.append(Article(**article))
                except Exception as e:
                    # Skip articles that don't match the Article schema
                    print(f"Error processing article: {e}")
                    continue
                    
            return article_objects
            
        except Exception as e:
            print(f"Error fetching articles for category {category}: {e}")
            return []
