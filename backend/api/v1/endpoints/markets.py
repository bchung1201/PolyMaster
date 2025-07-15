from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from services.polymarket_service import PolymarketService
from api.v1.models.requests.base import GetMarketsRequest, GetEventsRequest, MarketCategory
from api.v1.models.responses.base import (
    MarketsResponse, 
    EventsResponse, 
    MarketResponse, 
    EventResponse,
    OrderbookResponse,
    WalletBalanceResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Import dependency injection functions
from core.dependencies import get_polymarket_service

@router.get("/", response_model=MarketsResponse)
async def get_markets(
    limit: int = Query(default=20, ge=1, le=1000),
    category: Optional[MarketCategory] = Query(default=None),
    active_only: bool = Query(default=True),
    sort_by: str = Query(default="spread", description="Sort by: spread, volume, end_date"),
    tradeable_only: bool = Query(default=False, description="Only show tradeable markets"),
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get all markets with filtering and sorting"""
    try:
        if tradeable_only:
            markets_data = await polymarket_service.get_tradeable_markets(limit=limit)
        else:
            markets_data = await polymarket_service.get_all_markets(limit=limit)
        
        # Filter by category if specified
        if category:
            markets_data = [m for m in markets_data if m.get("category") == category.value]
        
        # Filter by active status
        if active_only:
            markets_data = [m for m in markets_data if m.get("active", False)]
        
        # Sort markets
        if sort_by == "spread":
            markets_data.sort(key=lambda x: x.get("spread", 0), reverse=True)
        elif sort_by == "volume":
            markets_data.sort(key=lambda x: x.get("volume", 0), reverse=True)
        elif sort_by == "end_date":
            markets_data.sort(key=lambda x: x.get("end", ""))
        
        # Convert to response models
        markets = [MarketResponse(**market) for market in markets_data]
        
        return MarketsResponse(
            markets=markets,
            total=len(markets),
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error getting markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=EventsResponse)
async def get_events(
    limit: int = Query(default=20, ge=1, le=100),
    category: Optional[MarketCategory] = Query(default=None),
    active_only: bool = Query(default=True),
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get all events with filtering"""
    try:
        events_data = await polymarket_service.get_all_events(limit=limit)
        
        # Convert to response models
        events = [EventResponse(**event) for event in events_data]
        
        return EventsResponse(
            events=events,
            total=len(events),
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{market_id}", response_model=MarketResponse)
async def get_market(
    market_id: str,
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get specific market by ID"""
    try:
        market_data = await polymarket_service.get_market_by_id(market_id)
        return MarketResponse(**market_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_events(
    limit: int = Query(default=50, ge=1, le=500),
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get events with their associated markets (sub-markets)"""
    try:
        events_data = await polymarket_service.get_events_with_markets(limit=limit)
        
        return {
            "events": events_data,
            "total": len(events_data),
            "timestamp": events_data[0].get("timestamp", "") if events_data else ""
        }
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{market_id}/orderbook", response_model=OrderbookResponse)
async def get_market_orderbook(
    market_id: str,
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get orderbook for a specific market"""
    try:
        # Get market data to find token IDs
        market_data = await polymarket_service.get_market_by_id(market_id)
        
        # Parse clob token IDs
        import ast
        token_ids = ast.literal_eval(market_data["clob_token_ids"])
        
        # Get orderbook for first token (YES token)
        orderbook = await polymarket_service.get_orderbook(token_ids[1])
        
        return OrderbookResponse(
            market=orderbook["market"],
            asset_id=orderbook["asset_id"],
            bids=orderbook["bids"],
            asks=orderbook["asks"],
            last_updated=market_data.get("last_updated", "")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting orderbook for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{market_id}/price")
async def get_market_price(
    market_id: str,
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get current price for a market"""
    try:
        # Get market data to find token IDs
        market_data = await polymarket_service.get_market_by_id(market_id)
        
        # Parse clob token IDs
        import ast
        token_ids = ast.literal_eval(market_data["clob_token_ids"])
        
        # Get prices for both tokens
        yes_price = await polymarket_service.get_market_price(token_ids[1])
        no_price = await polymarket_service.get_market_price(token_ids[0])
        
        return {
            "market_id": market_id,
            "yes_price": yes_price,
            "no_price": no_price,
            "last_updated": market_data.get("last_updated", "")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting price for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    polymarket_service: PolymarketService = Depends(get_polymarket_service)
):
    """Get wallet balance"""
    try:
        balance = await polymarket_service.get_wallet_balance()
        return WalletBalanceResponse(**balance)
        
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))