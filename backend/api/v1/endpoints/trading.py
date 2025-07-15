from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from services.trading_service import TradingService
from api.v1.models.requests.base import ExecuteTradeRequest, TradingStrategyRequest
from api.v1.models.responses.base import (
    TradeExecutionResponse,
    TradingOpportunitiesResponse,
    PortfolioResponse,
    TradingStrategyResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Import dependency injection functions
from core.dependencies import get_trading_service, get_news_service, get_ai_service

@router.get("/opportunities", response_model=TradingOpportunitiesResponse)
async def get_trading_opportunities(
    limit: int = Query(default=10, ge=1, le=50),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get current trading opportunities"""
    try:
        opportunities = await trading_service.get_trading_opportunities(limit=limit)
        
        return TradingOpportunitiesResponse(
            opportunities=opportunities,
            total=len(opportunities),
            timestamp=opportunities[0].get("timestamp", "") if opportunities else ""
        )
        
    except Exception as e:
        logger.error(f"Error getting trading opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=TradeExecutionResponse)
async def execute_trade(
    trade_request: ExecuteTradeRequest,
    trading_service: TradingService = Depends(get_trading_service)
):
    """Execute a trade"""
    try:
        result = await trading_service.execute_trade(
            market_id=trade_request.market_id,
            side=trade_request.side.value,
            amount=trade_request.amount,
            dry_run=trade_request.dry_run
        )
        
        return TradeExecutionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get current portfolio"""
    try:
        portfolio = await trading_service.get_portfolio()
        return PortfolioResponse(**portfolio)
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_trade_history(
    limit: int = Query(default=50, ge=1, le=100),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get trade history"""
    try:
        history = await trading_service.get_trade_history(limit=limit)
        
        return {
            "trades": history,
            "total": len(history),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategy", response_model=TradingStrategyResponse)
async def get_trading_strategy(
    strategy_request: TradingStrategyRequest,
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get AI trading strategy for a market"""
    try:
        # Get market data
        market_data = await trading_service.polymarket_service.get_market_by_id(
            strategy_request.market_id
        )
        
        # Get news data if requested
        news_data = []
        if strategy_request.include_news:
            news_service = get_news_service()
            news_data = await news_service.get_market_news(
                market_data["question"], 
                limit=5
            )
        
        # Get AI service
        ai_service = get_ai_service()
        
        strategy = await ai_service.get_trading_strategy(market_data, news_data)
        
        return TradingStrategyResponse(**strategy)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting trading strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{market_id}")
async def get_market_analysis(
    market_id: str,
    outcome: str = Query(default="yes", description="Outcome to analyze"),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Get AI analysis for a specific market"""
    try:
        analysis = await trading_service.get_ai_analysis(market_id, outcome)
        return analysis
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_trade(
    trade_request: ExecuteTradeRequest,
    trading_service: TradingService = Depends(get_trading_service)
):
    """Validate a trade without executing it"""
    try:
        # Get market data
        market_data = await trading_service.polymarket_service.get_market_by_id(
            trade_request.market_id
        )
        
        # Get wallet balance
        balance = await trading_service.polymarket_service.get_wallet_balance()
        
        # Validate trade
        validation_result = {
            "valid": True,
            "market_id": trade_request.market_id,
            "side": trade_request.side.value,
            "amount": trade_request.amount,
            "market_active": market_data.get("active", False),
            "market_funded": market_data.get("funded", False),
            "sufficient_balance": balance["usdc_balance"] >= trade_request.amount,
            "balance": balance["usdc_balance"],
            "warnings": [],
            "errors": []
        }
        
        # Check for issues
        if not market_data.get("active", False):
            validation_result["valid"] = False
            validation_result["errors"].append("Market is not active")
            
        if not market_data.get("funded", False):
            validation_result["valid"] = False
            validation_result["errors"].append("Market is not funded")
            
        if balance["usdc_balance"] < trade_request.amount:
            validation_result["valid"] = False
            validation_result["errors"].append("Insufficient USDC balance")
            
        if trade_request.amount < market_data.get("rewardsMinSize", 0):
            validation_result["warnings"].append(
                f"Trade amount is below minimum reward size: {market_data.get('rewardsMinSize', 0)}"
            )
            
        return validation_result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autonomous")
async def run_autonomous_trading(
    dry_run: bool = Query(default=True, description="Run in dry run mode"),
    trading_service: TradingService = Depends(get_trading_service)
):
    """Run one cycle of autonomous AI trading from trader.py"""
    try:
        result = await trading_service.run_autonomous_trading(dry_run=dry_run)
        return result
        
    except Exception as e:
        logger.error(f"Error running autonomous trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))