from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging

from core.auth.models import User
from core.auth.service import AuthService
from services.user_trading_service import UserTradingService
from api.v1.models.requests.base import ExecuteTradeRequest
from api.v1.endpoints.auth import get_current_user_dependency

logger = logging.getLogger(__name__)
router = APIRouter()
auth_service = AuthService()

@router.get("/portfolio")
async def get_user_portfolio(
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current user's portfolio"""
    try:
        if not current_user.clob_api_key:
            raise HTTPException(
                status_code=400,
                detail="Wallet not configured. Please configure your wallet credentials first."
            )
        
        user_trading_service = UserTradingService(current_user, auth_service)
        portfolio = await user_trading_service.get_user_portfolio()
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Error getting portfolio for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_user_trade(
    trade_request: ExecuteTradeRequest,
    current_user: User = Depends(get_current_user_dependency)
):
    """Execute a trade for the current user"""
    try:
        if not current_user.clob_api_key:
            raise HTTPException(
                status_code=400,
                detail="Wallet not configured. Please configure your wallet credentials first."
            )
        
        user_trading_service = UserTradingService(current_user, auth_service)
        
        result = await user_trading_service.execute_user_trade(
            market_id=trade_request.market_id,
            side=trade_request.side.value,
            amount=trade_request.amount,
            dry_run=trade_request.dry_run
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing trade for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_user_trade_history(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get user's trade history"""
    try:
        user_trading_service = UserTradingService(current_user, auth_service)
        history = await user_trading_service.get_user_trade_history(limit=limit)
        
        return {
            "trades": history,
            "total": len(history),
            "user_id": current_user.id,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting trade history for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{market_id}")
async def get_user_market_recommendation(
    market_id: str,
    current_user: User = Depends(get_current_user_dependency)
):
    """Get AI recommendation for a market, personalized for the user"""
    try:
        user_trading_service = UserTradingService(current_user, auth_service)
        recommendation = await user_trading_service.get_ai_recommendation_for_user(market_id)
        
        return recommendation
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recommendation for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_user_trade(
    trade_request: ExecuteTradeRequest,
    current_user: User = Depends(get_current_user_dependency)
):
    """Validate a trade for the current user"""
    try:
        if not current_user.clob_api_key:
            return {
                "valid": False,
                "errors": ["Wallet not configured"],
                "warnings": []
            }
        
        user_trading_service = UserTradingService(current_user, auth_service)
        
        # Get market data
        market_data = await user_trading_service.get_market_by_id(trade_request.market_id)
        
        # Get user portfolio
        portfolio = await user_trading_service.get_user_portfolio()
        balance = portfolio["balance"]["usdc_balance"]
        
        # Validate trade
        validation_result = {
            "valid": True,
            "market_id": trade_request.market_id,
            "side": trade_request.side.value,
            "amount": trade_request.amount,
            "user_id": current_user.id,
            "market_active": market_data.get("active", False),
            "market_funded": market_data.get("funded", False),
            "sufficient_balance": balance >= trade_request.amount,
            "within_user_limits": trade_request.amount <= current_user.max_trade_amount,
            "balance": balance,
            "user_max_amount": current_user.max_trade_amount,
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
            
        if balance < trade_request.amount:
            validation_result["valid"] = False
            validation_result["errors"].append("Insufficient USDC balance")
            
        if trade_request.amount > current_user.max_trade_amount:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Trade amount exceeds your maximum limit of {current_user.max_trade_amount} USDC")
            
        if trade_request.amount < market_data.get("rewardsMinSize", 0):
            validation_result["warnings"].append(
                f"Trade amount is below minimum reward size: {market_data.get('rewardsMinSize', 0)}"
            )
        
        # Risk tolerance warnings
        if current_user.risk_tolerance == "low" and trade_request.amount > current_user.max_trade_amount * 0.1:
            validation_result["warnings"].append(
                "Large trade amount for conservative risk tolerance"
            )
            
        return validation_result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error validating trade for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings")
async def update_user_trading_settings(
    max_trade_amount: Optional[int] = None,
    risk_tolerance: Optional[str] = None,
    default_dry_run: Optional[bool] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_database_session)
):
    """Update user's trading settings"""
    try:
        if max_trade_amount is not None:
            if max_trade_amount < 1 or max_trade_amount > 10000:
                raise HTTPException(
                    status_code=400,
                    detail="Max trade amount must be between 1 and 10,000 USDC"
                )
            current_user.max_trade_amount = max_trade_amount
        
        if risk_tolerance is not None:
            if risk_tolerance not in ["low", "medium", "high"]:
                raise HTTPException(
                    status_code=400,
                    detail="Risk tolerance must be 'low', 'medium', or 'high'"
                )
            current_user.risk_tolerance = risk_tolerance
        
        if default_dry_run is not None:
            current_user.default_dry_run = default_dry_run
        
        db.commit()
        
        return {
            "message": "Trading settings updated successfully",
            "settings": {
                "max_trade_amount": current_user.max_trade_amount,
                "risk_tolerance": current_user.risk_tolerance,
                "default_dry_run": current_user.default_dry_run
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating settings")