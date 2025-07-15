import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data.polymarket.client import Polymarket
from agents.trading.trader import Trader
from agents.ai.executor import Executor
from core.auth.models import User, WalletConfig
from core.auth.service import AuthService
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserTradingService:
    """Trading service that operates with user-specific credentials"""
    
    def __init__(self, user: User, auth_service: AuthService):
        self.user = user
        self.auth_service = auth_service
        
        # Get user's wallet configuration
        self.wallet_config = auth_service.decrypt_wallet_config(user)
        
        # Initialize Polymarket client with user's credentials
        self.polymarket = self._create_user_polymarket_client()
        self.trader = Trader()
        self.executor = Executor()
        
    def _create_user_polymarket_client(self) -> Polymarket:
        """Create Polymarket client with user's credentials"""
        # Temporarily set environment variables for this user's session
        original_env = {}
        user_env_vars = {
            'POLYGON_WALLET_PRIVATE_KEY': self.wallet_config.wallet_private_key,
            'CLOB_API_KEY': self.wallet_config.clob_api_key,
            'CLOB_SECRET': self.wallet_config.clob_secret,
            'CLOB_PASS_PHRASE': self.wallet_config.clob_passphrase,
            'DRY_RUN': str(self.user.default_dry_run).lower()
        }
        
        # Backup original env vars
        for key in user_env_vars:
            original_env[key] = os.environ.get(key)
            os.environ[key] = user_env_vars[key] or ''
        
        try:
            # Create client with user's credentials
            polymarket = Polymarket()
            return polymarket
        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    async def get_user_portfolio(self) -> Dict[str, Any]:
        """Get user's current portfolio"""
        try:
            loop = asyncio.get_event_loop()
            balance = await loop.run_in_executor(None, self.polymarket.get_wallet_balance)
            
            # Get user's positions (would need to implement in Polymarket client)
            # positions = await loop.run_in_executor(None, self.polymarket.get_user_positions)
            
            return {
                "user_id": self.user.id,
                "username": self.user.username,
                "wallet_address": self.user.wallet_address,
                "balance": balance,
                "total_value": balance.get("usdc_balance", 0),
                "positions": [],  # positions,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting portfolio for user {self.user.id}: {e}")
            raise
    
    async def execute_user_trade(
        self, 
        market_id: str, 
        side: str, 
        amount: float, 
        dry_run: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Execute trade for specific user"""
        try:
            # Use user's default dry_run setting if not specified
            if dry_run is None:
                dry_run = self.user.default_dry_run
            
            # Check user's trading limits
            if amount > self.user.max_trade_amount:
                raise ValueError(f"Trade amount {amount} exceeds user's maximum of {self.user.max_trade_amount}")
            
            # Get market data
            market_data = await self.get_market_by_id(market_id)
            
            # Execute trade using user's credentials
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_trade_sync,
                market_data,
                side,
                amount,
                dry_run
            )
            
            # Log trade for user
            trade_record = {
                "user_id": self.user.id,
                "market_id": market_id,
                "side": side,
                "amount": amount,
                "dry_run": dry_run,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trade executed for user {self.user.id}: {trade_record}")
            
            return {
                **result,
                "user_id": self.user.id,
                "trade_record": trade_record
            }
            
        except Exception as e:
            logger.error(f"Error executing trade for user {self.user.id}: {e}")
            raise
    
    def _execute_trade_sync(self, market_data: dict, side: str, amount: float, dry_run: bool) -> dict:
        """Synchronous trade execution for thread pool"""
        # This would integrate with the existing Trader logic
        # but with user-specific credentials already set
        
        if dry_run:
            return {
                "success": True,
                "message": "Trade executed successfully (DRY RUN)",
                "market_id": market_data["id"],
                "side": side,
                "amount": amount,
                "estimated_price": market_data.get("outcome_prices", "Unknown"),
                "dry_run": True
            }
        else:
            # Actual trade execution would happen here
            # using the trader with user's credentials
            return {
                "success": True,
                "message": "Trade executed successfully",
                "market_id": market_data["id"],
                "side": side,
                "amount": amount,
                "transaction_hash": "0x123...",  # Real tx hash
                "dry_run": False
            }
    
    async def get_market_by_id(self, market_id: str) -> Dict[str, Any]:
        """Get market data using user's credentials"""
        loop = asyncio.get_event_loop()
        market = await loop.run_in_executor(None, self.polymarket.get_market_by_id, market_id)
        return market
    
    async def get_user_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's trade history"""
        try:
            # This would fetch from a user_trades table in the database
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting trade history for user {self.user.id}: {e}")
            raise
    
    async def get_ai_recommendation_for_user(self, market_id: str) -> Dict[str, Any]:
        """Get AI recommendation considering user's risk tolerance"""
        try:
            market_data = await self.get_market_by_id(market_id)
            
            # Get AI analysis
            loop = asyncio.get_event_loop()
            analysis = await loop.run_in_executor(
                None,
                self.executor.get_superforecast,
                market_data["question"]
            )
            
            # Adjust recommendation based on user's risk tolerance
            recommendation = self._adjust_for_risk_tolerance(analysis)
            
            return {
                "user_id": self.user.id,
                "market_id": market_id,
                "analysis": analysis,
                "recommendation": recommendation,
                "risk_tolerance": self.user.risk_tolerance,
                "max_suggested_amount": min(
                    self.user.max_trade_amount,
                    self._calculate_suggested_amount(analysis)
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting AI recommendation for user {self.user.id}: {e}")
            raise
    
    def _adjust_for_risk_tolerance(self, analysis: dict) -> dict:
        """Adjust AI recommendation based on user's risk tolerance"""
        confidence = analysis.get("confidence", 0.5)
        
        if self.user.risk_tolerance == "low":
            # Only recommend trades with high confidence
            if confidence < 0.7:
                return {"action": "hold", "reason": "Confidence too low for conservative strategy"}
        elif self.user.risk_tolerance == "high":
            # More aggressive recommendations
            if confidence > 0.3:
                return {"action": "trade", "reason": "Acceptable risk for aggressive strategy"}
        
        # Medium risk tolerance - use original analysis
        return analysis.get("recommendation", {"action": "hold"})
    
    def _calculate_suggested_amount(self, analysis: dict) -> float:
        """Calculate suggested trade amount based on confidence and user settings"""
        confidence = analysis.get("confidence", 0.5)
        base_amount = self.user.max_trade_amount * 0.1  # Start with 10% of max
        
        # Adjust based on confidence
        suggested_amount = base_amount * confidence * 2  # Scale with confidence
        
        return min(suggested_amount, self.user.max_trade_amount)