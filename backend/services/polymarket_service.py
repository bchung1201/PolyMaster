import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data.polymarket.client import Polymarket
from agents.models.schemas import SimpleMarket, SimpleEvent
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PolymarketService:
    def __init__(self):
        self.polymarket = Polymarket()
        self.cache = {}
        self.cache_timeout = 60  # seconds
        
    async def get_all_markets(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all markets with caching"""
        try:
            cache_key = f"all_markets_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            markets = await loop.run_in_executor(None, self.polymarket.get_all_markets)
            
            # Convert to dict format for JSON serialization
            markets_data = []
            for market in markets[:limit]:
                market_dict = {
                    "id": market.id,
                    "question": market.question,
                    "end": market.end,
                    "description": market.description,
                    "active": market.active,
                    "funded": market.funded,
                    "rewardsMinSize": market.rewardsMinSize,
                    "rewardsMaxSpread": market.rewardsMaxSpread,
                    "spread": market.spread,
                    "outcomes": market.outcomes,
                    "outcome_prices": market.outcome_prices,
                    "clob_token_ids": market.clob_token_ids,
                    "category": self.polymarket.detect_category(market.question)
                }
                markets_data.append(market_dict)
                
            self._set_cache(cache_key, markets_data)
            return markets_data
            
        except Exception as e:
            logger.error(f"Error getting markets: {e}")
            raise
            
    async def get_tradeable_markets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get markets suitable for trading"""
        try:
            cache_key = f"tradeable_markets_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            loop = asyncio.get_event_loop()
            markets = await loop.run_in_executor(None, self.polymarket.get_all_markets)
            tradeable = await loop.run_in_executor(None, self.polymarket.filter_markets_for_trading, markets)
            
            # Sort by spread (highest first)
            tradeable.sort(key=lambda x: x.spread, reverse=True)
            
            markets_data = []
            for market in tradeable[:limit]:
                market_dict = {
                    "id": market.id,
                    "question": market.question,
                    "end": market.end,
                    "description": market.description,
                    "active": market.active,
                    "funded": market.funded,
                    "rewardsMinSize": market.rewardsMinSize,
                    "rewardsMaxSpread": market.rewardsMaxSpread,
                    "spread": market.spread,
                    "outcomes": market.outcomes,
                    "outcome_prices": market.outcome_prices,
                    "clob_token_ids": market.clob_token_ids,
                    "category": self.polymarket.detect_category(market.question)
                }
                markets_data.append(market_dict)
                
            self._set_cache(cache_key, markets_data)
            return markets_data
            
        except Exception as e:
            logger.error(f"Error getting tradeable markets: {e}")
            raise
            
    async def get_market_by_id(self, market_id: str) -> Dict[str, Any]:
        """Get specific market by ID"""
        try:
            cache_key = f"market_{market_id}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            loop = asyncio.get_event_loop()
            market = await loop.run_in_executor(None, self.polymarket.get_market, market_id)
            
            if market:
                market_dict = {
                    "id": market["id"],
                    "question": market["question"],
                    "end": market["end"],
                    "description": market["description"],
                    "active": market["active"],
                    "funded": market["funded"],
                    "rewardsMinSize": market["rewardsMinSize"],
                    "rewardsMaxSpread": market["rewardsMaxSpread"],
                    "spread": market["spread"],
                    "outcomes": market["outcomes"],
                    "outcome_prices": market["outcome_prices"],
                    "clob_token_ids": market["clob_token_ids"],
                    "category": self.polymarket.detect_category(market["question"])
                }
                self._set_cache(cache_key, market_dict)
                return market_dict
            else:
                raise ValueError(f"Market {market_id} not found")
                
        except Exception as e:
            logger.error(f"Error getting market {market_id}: {e}")
            raise
            
    async def get_all_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all events"""
        try:
            cache_key = f"all_events_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            loop = asyncio.get_event_loop()
            events = await loop.run_in_executor(None, self.polymarket.get_all_events)
            
            events_data = []
            for event in events[:limit]:
                event_dict = {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "markets": event.markets,
                    "metadata": event.metadata
                }
                events_data.append(event_dict)
                
            self._set_cache(cache_key, events_data)
            return events_data
            
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            raise
            
    async def get_orderbook(self, token_id: str) -> Dict[str, Any]:
        """Get orderbook for a token"""
        try:
            loop = asyncio.get_event_loop()
            orderbook = await loop.run_in_executor(None, self.polymarket.get_orderbook, token_id)
            
            return {
                "market": orderbook.market,
                "asset_id": orderbook.asset_id,
                "bids": [{"price": bid.price, "size": bid.size} for bid in orderbook.bids],
                "asks": [{"price": ask.price, "size": ask.size} for ask in orderbook.asks]
            }
            
        except Exception as e:
            logger.error(f"Error getting orderbook for {token_id}: {e}")
            raise
            
    async def get_market_price(self, token_id: str) -> float:
        """Get current market price for a token"""
        try:
            loop = asyncio.get_event_loop()
            price = await loop.run_in_executor(None, self.polymarket.get_orderbook_price, token_id)
            return price
            
        except Exception as e:
            logger.error(f"Error getting price for {token_id}: {e}")
            raise
            
    async def get_wallet_balance(self) -> Dict[str, Any]:
        """Get wallet balance information"""
        try:
            loop = asyncio.get_event_loop()
            usdc_balance = await loop.run_in_executor(None, self.polymarket.get_usdc_balance)
            
            return {
                "usdc_balance": usdc_balance,
                "wallet_address": self.polymarket.wallet_address,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            raise
            
    async def get_events_with_markets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events with their associated markets (sub-markets)"""
        try:
            cache_key = f"events_with_markets_{limit}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]["data"]
                
            from agents.data.polymarket.gamma import GammaMarketClient
            gamma = GammaMarketClient()
            
            # Get events from Gamma API
            loop = asyncio.get_event_loop()
            events_data = await loop.run_in_executor(
                None, 
                gamma.get_events, 
                {"limit": limit, "archived": "false", "closed": "false"}
            )
            
            events_with_markets = []
            for event in events_data[:limit]:
                try:
                    event_dict = {
                        "id": event.get("id"),
                        "title": event.get("title", ""),
                        "description": event.get("description", ""),
                        "slug": event.get("slug", ""),
                        "tags": event.get("tags", []),
                        "startDate": event.get("startDate"),
                        "endDate": event.get("endDate"),
                        "image": event.get("image"),
                        "markets": [],
                        "category": self.polymarket.detect_category(event.get("title", "")),
                        "timestamp": event.get("createdAt", "")
                    }
                    
                    # Get markets for this event
                    if "markets" in event and event["markets"]:
                        for market in event["markets"][:10]:  # Limit sub-markets
                            try:
                                market_dict = {
                                    "id": market.get("id"),
                                    "question": market.get("question", ""),
                                    "description": market.get("description", ""),
                                    "outcomes": market.get("outcomes", []),
                                    "outcome_prices": market.get("outcomePrices", "[]"),
                                    "clob_token_ids": market.get("clobTokenIds", "[]"),
                                    "volume": float(market.get("volume", 0)),
                                    "liquidity": float(market.get("liquidity", 0)),
                                    "spread": float(market.get("spread", 0)),
                                    "active": market.get("active", True),
                                    "funded": market.get("funded", True),
                                    "end": market.get("endDate"),
                                    "category": self.polymarket.detect_category(market.get("question", ""))
                                }
                                event_dict["markets"].append(market_dict)
                            except Exception as market_error:
                                logger.warning(f"Error processing market in event {event.get('id')}: {market_error}")
                                continue
                    
                    # Only include events that have markets
                    if event_dict["markets"]:
                        events_with_markets.append(event_dict)
                        
                except Exception as event_error:
                    logger.warning(f"Error processing event {event.get('id')}: {event_error}")
                    continue
            
            # Sort by number of markets (most diverse events first)
            events_with_markets.sort(key=lambda x: len(x["markets"]), reverse=True)
            
            self._set_cache(cache_key, events_with_markets)
            return events_with_markets
            
        except Exception as e:
            logger.error(f"Error getting events with markets: {e}")
            raise
            
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