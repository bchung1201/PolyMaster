import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_subscribers: List[WebSocket] = []
        self.news_subscribers: List[WebSocket] = []
        self.ai_subscribers: List[WebSocket] = []
        self.running = False
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.market_subscribers:
            self.market_subscribers.remove(websocket)
        if websocket in self.news_subscribers:
            self.news_subscribers.remove(websocket)
        if websocket in self.ai_subscribers:
            self.ai_subscribers.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast_to_subscribers(self, message: dict, subscribers: List[WebSocket]):
        disconnected = []
        for websocket in subscribers:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(websocket)
                
        # Remove disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
            
    async def subscribe_to_markets(self, websocket: WebSocket):
        if websocket not in self.market_subscribers:
            self.market_subscribers.append(websocket)
            await self.send_personal_message({
                "type": "subscription_confirmed",
                "channel": "markets",
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
    async def subscribe_to_news(self, websocket: WebSocket):
        if websocket not in self.news_subscribers:
            self.news_subscribers.append(websocket)
            await self.send_personal_message({
                "type": "subscription_confirmed", 
                "channel": "news",
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
    async def get_ai_analysis(self, websocket: WebSocket, market_id: str):
        # This will be implemented to stream AI analysis
        await self.send_personal_message({
            "type": "ai_analysis_started",
            "market_id": market_id,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # TODO: Implement actual AI analysis streaming
        await asyncio.sleep(2)  # Simulate processing time
        
        await self.send_personal_message({
            "type": "ai_analysis_complete",
            "market_id": market_id,
            "analysis": "AI analysis placeholder - to be implemented",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    async def start_market_updates(self):
        """Background task to send market updates"""
        self.running = True
        while self.running:
            try:
                if self.market_subscribers:
                    # TODO: Get real market data
                    market_update = {
                        "type": "market_update",
                        "data": {
                            "timestamp": datetime.now().isoformat(),
                            "markets": "placeholder - to be implemented"
                        }
                    }
                    await self.broadcast_to_subscribers(market_update, self.market_subscribers)
                    
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in market updates: {e}")
                await asyncio.sleep(10)
                
    async def start_news_updates(self):
        """Background task to send news updates"""
        while self.running:
            try:
                if self.news_subscribers:
                    # TODO: Get real news data
                    news_update = {
                        "type": "news_update",
                        "data": {
                            "timestamp": datetime.now().isoformat(),
                            "articles": "placeholder - to be implemented"
                        }
                    }
                    await self.broadcast_to_subscribers(news_update, self.news_subscribers)
                    
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in news updates: {e}")
                await asyncio.sleep(60)
                
    def stop(self):
        self.running = False