"""
Dependency injection for FastAPI endpoints
Avoids circular imports by providing a central place for service dependencies
"""

from fastapi import HTTPException
from typing import Optional

# Global service instances (set by main app)
_polymarket_service = None
_trading_service = None
_news_service = None
_ai_service = None
_websocket_manager = None

def set_services(polymarket_service, trading_service, news_service, ai_service, websocket_manager):
    """Set service instances from main app (called during startup)"""
    global _polymarket_service, _trading_service, _news_service, _ai_service, _websocket_manager
    _polymarket_service = polymarket_service
    _trading_service = trading_service
    _news_service = news_service
    _ai_service = ai_service
    _websocket_manager = websocket_manager

def get_polymarket_service():
    """Get polymarket service instance"""
    if _polymarket_service is None:
        raise HTTPException(status_code=503, detail="Polymarket service not available")
    return _polymarket_service

def get_trading_service():
    """Get trading service instance"""
    if _trading_service is None:
        raise HTTPException(status_code=503, detail="Trading service not available")
    return _trading_service

def get_news_service():
    """Get news service instance"""
    if _news_service is None:
        raise HTTPException(status_code=503, detail="News service not available")
    return _news_service

def get_ai_service():
    """Get AI service instance"""
    if _ai_service is None:
        raise HTTPException(status_code=503, detail="AI service not available")
    return _ai_service

def get_websocket_manager():
    """Get websocket manager instance"""
    if _websocket_manager is None:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")
    return _websocket_manager