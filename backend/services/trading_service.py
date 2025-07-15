import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trading.trader import Trader
from agents.ai.executor import Executor
from agents.models.schemas import SimpleMarket, SimpleEvent
from services.polymarket_service import PolymarketService
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TradingService:
    def __init__(self, polymarket_service: PolymarketService):
        self.polymarket_service = polymarket_service
        self.trader = Trader()
        self.executor = Executor()
        
    async def run_autonomous_trading(self, dry_run: bool = True) -> Dict[str, Any]:
        """Run one cycle of autonomous trading from trader.py"""
        try:
            # Set dry run mode for trader
            original_dry_run = self.trader.dry_run
            self.trader.dry_run = dry_run
            
            # Use trader's pre_trade_logic
            self.trader.pre_trade_logic()
            
            # Get high quality events (mimicking trader.py logic)
            loop = asyncio.get_event_loop()
            events = await loop.run_in_executor(
                None,
                self.trader.polymarket.get_all_events
            )
            
            logger.info(f"Found {len(events)} total events")
            
            # Filter events using trader's logic
            high_quality_events = []
            for event in events:
                try:
                    event_data = event.dict()
                    market_ids = event_data.get('markets', '').split(',')
                    
                    for market_id in market_ids:
                        if not market_id:
                            continue
                            
                        market_data = self.trader.gamma.get_market(market_id)
                        volume = float(market_data.get('volume', 0))
                        is_pinned = market_data.get('featured', False)
                        
                        if volume > 10000 or is_pinned:
                            event_with_trade = {
                                'event': event,
                                'trade': {
                                    'market_data': market_data
                                }
                            }
                            high_quality_events.append((event_with_trade, 1.0))
                            break
                            
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    continue
            
            logger.info(f"Found {len(high_quality_events)} high quality events")
            
            if not high_quality_events:
                return {
                    "success": False,
                    "message": "No high quality events found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Filter events with RAG
            filtered_events = await loop.run_in_executor(
                None,
                self.trader.agent.filter_events_with_rag,
                high_quality_events
            )
            
            logger.info(f"Filtered to {len(filtered_events)} events")
            
            # Map to markets
            markets = await loop.run_in_executor(
                None,
                self.trader.agent.map_filtered_events_to_markets,
                filtered_events
            )
            
            logger.info(f"Found {len(markets)} markets")
            
            # Filter markets
            filtered_markets = await loop.run_in_executor(
                None,
                self.trader.agent.filter_markets,
                markets
            )
            
            logger.info(f"Filtered to {len(filtered_markets)} markets")
            
            # Analyze markets and find best trade
            for market_tuple in filtered_markets:
                try:
                    market_data = market_tuple[0]  # SimpleMarket
                    
                    if not hasattr(market_data, 'clob_token_ids') or not market_data.clob_token_ids:
                        continue
                    
                    # Get AI trading decision
                    best_trade = await loop.run_in_executor(
                        None,
                        self.trader.agent.source_best_trade,
                        market_tuple
                    )
                    
                    if best_trade and isinstance(best_trade, dict):
                        target_price = float(best_trade.get('price', 0))
                        edge = best_trade.get('edge', 0)
                        position = best_trade.get('position', 'UNKNOWN')
                        
                        logger.info(f"AI Decision for {market_data.question}: BUY {position} at ${target_price}, Edge: {edge:.4f}")
                        
                        if dry_run:
                            return {
                                "success": True,
                                "trade_decision": {
                                    "market_question": market_data.question,
                                    "action": f"BUY {position}",
                                    "target_price": target_price,
                                    "edge": edge,
                                    "confidence": best_trade.get('confidence', 0),
                                    "reasoning": best_trade.get('prediction', ''),
                                    "analysis": best_trade.get('analysis', '')
                                },
                                "dry_run": True,
                                "message": "Trade decision generated (DRY RUN mode)",
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            # Execute real trade
                            amount = 1.0  # $1 USDC for testing
                            trade_result = await loop.run_in_executor(
                                None,
                                self.trader.polymarket.execute_market_order,
                                market_data,
                                amount
                            )
                            
                            return {
                                "success": trade_result is not None,
                                "trade_decision": {
                                    "market_question": market_data.question,
                                    "action": f"BUY {position}",
                                    "target_price": target_price,
                                    "amount": amount,
                                    "edge": edge,
                                    "confidence": best_trade.get('confidence', 0)
                                },
                                "trade_result": trade_result,
                                "dry_run": False,
                                "timestamp": datetime.now().isoformat()
                            }
                            
                except Exception as e:
                    logger.error(f"Error analyzing market: {e}")
                    continue
            
            return {
                "success": False,
                "message": "No eligible trades found",
                "markets_analyzed": len(filtered_markets),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous trading: {e}")
            raise
        finally:
            # Restore original dry run setting
            self.trader.dry_run = original_dry_run
        
    async def get_trading_opportunities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current trading opportunities using AI analysis from trader.py"""
        try:
            # Get tradeable markets
            markets = await self.polymarket_service.get_tradeable_markets(limit=limit)
            
            opportunities = []
            for market in markets:
                # Convert to SimpleMarket object for analysis
                simple_market = SimpleMarket(
                    id=market["id"],
                    question=market["question"],
                    end=market["end"],
                    description=market["description"],
                    active=market["active"],
                    funded=market["funded"],
                    rewardsMinSize=market["rewardsMinSize"],
                    rewardsMaxSpread=market["rewardsMaxSpread"],
                    spread=market["spread"],
                    outcomes=market["outcomes"],
                    outcome_prices=market["outcome_prices"],
                    clob_token_ids=market["clob_token_ids"]
                )
                
                # Use trader's AI analysis pipeline from trader.py
                loop = asyncio.get_event_loop()
                market_tuple = (simple_market, 1.0)
                best_trade = await loop.run_in_executor(
                    None,
                    self.trader.agent.source_best_trade,
                    market_tuple
                )
                
                if best_trade and isinstance(best_trade, dict):
                    opportunity = {
                        "market": market,
                        "ai_decision": {
                            "action": f"BUY {best_trade.get('position', 'UNKNOWN')}",
                            "position": best_trade.get('position'),
                            "target_price": float(best_trade.get('price', 0)),
                            "edge": best_trade.get('edge', 0),
                            "confidence": best_trade.get('confidence', 0),
                            "reasoning": best_trade.get('prediction', 'No prediction available'),
                            "analysis": best_trade.get('analysis', '')
                        },
                        "category": market.get("category", "unknown"),
                        "spread": market["spread"],
                        "priority": self._calculate_ai_priority(market, best_trade)
                    }
                    opportunities.append(opportunity)
                
            # Sort by AI priority
            opportunities.sort(key=lambda x: x["priority"], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error getting trading opportunities: {e}")
            raise
            
    async def execute_trade(self, market_id: str, side: str, amount: float, dry_run: bool = True) -> Dict[str, Any]:
        """Execute a trade using trader.py logic"""
        try:
            # Get market data
            market_data = await self.polymarket_service.get_market_by_id(market_id)
            
            # Convert to SimpleMarket object
            simple_market = SimpleMarket(
                id=market_data["id"],
                question=market_data["question"],
                end=market_data["end"],
                description=market_data["description"],
                active=market_data["active"],
                funded=market_data["funded"],
                rewardsMinSize=market_data["rewardsMinSize"],
                rewardsMaxSpread=market_data["rewardsMaxSpread"],
                spread=market_data["spread"],
                outcomes=market_data["outcomes"],
                outcome_prices=market_data["outcome_prices"],
                clob_token_ids=market_data["clob_token_ids"]
            )
            
            if dry_run:
                # Simulate trade execution
                return {
                    "success": True,
                    "result": "DRY_RUN_SIMULATION",
                    "market_id": market_id,
                    "side": side,
                    "amount": amount,
                    "dry_run": True,
                    "message": "Trade simulated successfully (DRY RUN mode)",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute real trade using trader's polymarket client
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.trader.polymarket.execute_market_order,
                simple_market,
                amount
            )
            
            return {
                "success": result is not None,
                "result": result,
                "market_id": market_id,
                "side": side,
                "amount": amount,
                "dry_run": dry_run,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise
            
    async def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio information"""
        try:
            # Get wallet balance
            balance = await self.polymarket_service.get_wallet_balance()
            
            # TODO: Get positions from blockchain
            positions = []
            
            return {
                "balance": balance,
                "positions": positions,
                "total_value": balance["usdc_balance"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            raise
            
    async def get_trade_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trade history"""
        try:
            # TODO: Implement trade history from database or blockchain
            return []
            
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            raise
            
    async def get_ai_analysis(self, market_id: str, outcome: str = "yes") -> Dict[str, Any]:
        """Get AI analysis for a specific market using trader.py logic"""
        try:
            market_data = await self.polymarket_service.get_market_by_id(market_id)
            
            # Convert to SimpleMarket for trader analysis
            simple_market = SimpleMarket(
                id=market_data["id"],
                question=market_data["question"],
                end=market_data["end"],
                description=market_data["description"],
                active=market_data["active"],
                funded=market_data["funded"],
                rewardsMinSize=market_data["rewardsMinSize"],
                rewardsMaxSpread=market_data["rewardsMaxSpread"],
                spread=market_data["spread"],
                outcomes=market_data["outcomes"],
                outcome_prices=market_data["outcome_prices"],
                clob_token_ids=market_data["clob_token_ids"]
            )
            
            # Use trader's AI analysis pipeline
            loop = asyncio.get_event_loop()
            market_tuple = (simple_market, 1.0)
            best_trade = await loop.run_in_executor(
                None,
                self.trader.agent.source_best_trade,
                market_tuple
            )
            
            if best_trade and isinstance(best_trade, dict):
                return {
                    "market_id": market_id,
                    "analysis": best_trade.get('analysis', ''),
                    "prediction": best_trade.get('prediction', ''),
                    "ai_decision": {
                        "action": f"BUY {best_trade.get('position', 'UNKNOWN')}",
                        "position": best_trade.get('position'),
                        "target_price": float(best_trade.get('price', 0)),
                        "edge": best_trade.get('edge', 0),
                        "confidence": best_trade.get('confidence', 0)
                    },
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback to simple analysis if no trade decision
                analysis = await loop.run_in_executor(
                    None,
                    self.executor.get_superforecast,
                    market_data["question"],
                    market_data["question"],
                    outcome
                )
                
                return {
                    "market_id": market_id,
                    "analysis": analysis,
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            raise
            
    def _calculate_priority(self, market: Dict[str, Any], analysis: str) -> float:
        """Calculate priority score for trading opportunity"""
        try:
            priority = 0.0
            
            # Base priority on spread
            priority += market["spread"] * 10
            
            # Add bonus for funded markets
            if market["funded"]:
                priority += 5
                
            # Add bonus for active markets
            if market["active"]:
                priority += 3
                
            # TODO: Parse analysis for confidence score
            if "high confidence" in analysis.lower():
                priority += 10
            elif "medium confidence" in analysis.lower():
                priority += 5
                
            return priority
            
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 0.0
            
    def _calculate_ai_priority(self, market: Dict[str, Any], best_trade: Dict[str, Any]) -> float:
        """Calculate priority using AI trading analysis from trader.py"""
        try:
            priority = 0.0
            
            # Base priority on edge (how much AI thinks market is mispriced)
            edge = best_trade.get('edge', 0)
            priority += edge * 100  # Scale edge to priority points
            
            # Add bonus for AI confidence
            confidence = best_trade.get('confidence', 0)
            priority += confidence * 50
            
            # Add bonus for funded and active markets
            if market.get("funded"):
                priority += 10
            if market.get("active"):
                priority += 5
                
            # Bonus for larger spreads (more liquid markets)
            priority += market.get("spread", 0) * 10
            
            return priority
            
        except Exception as e:
            logger.error(f"Error calculating AI priority: {e}")
            return 0.0