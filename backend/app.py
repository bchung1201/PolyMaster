from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Import our services
from services.polymarket_service import PolymarketService
from services.trading_service import TradingService
from services.news_service import NewsService
from services.ai_service import AIService
from core.websocket.manager import WebSocketManager
from core.config.settings import settings
from core.dependencies import set_services

# Import API routers
from api.v1.endpoints.markets import router as markets_router
from api.v1.endpoints.trading import router as trading_router
from api.v1.endpoints.news import router as news_router
from api.v1.endpoints.ai import router as ai_router

load_dotenv()

# Global services
polymarket_service = None
trading_service = None
news_service = None
ai_service = None
websocket_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global polymarket_service, trading_service, news_service, ai_service, websocket_manager
    
    print("🚀 Starting PolyMaster with AI Trading Bot...")
    
    # Initialize services
    polymarket_service = PolymarketService()
    trading_service = TradingService(polymarket_service)
    news_service = NewsService()
    ai_service = AIService()
    websocket_manager = WebSocketManager()
    
    # Set global services for dependency injection
    set_services(polymarket_service, trading_service, news_service, ai_service, websocket_manager)
    
    print("✅ AI Trading Bot integrated from trader.py")
    print("🔍 DRY_RUN mode enabled by default for safety")
    
    # Start background tasks
    asyncio.create_task(websocket_manager.start_market_updates())
    asyncio.create_task(websocket_manager.start_news_updates())
    
    print("✅ PolyAgent Web started successfully!")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down PolyAgent Web...")

app = FastAPI(
    title="PolyMaster",
    description="AI-powered prediction market trading platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow Vercel and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://poly-master.vercel.app",
        "https://polymaster.vercel.app",
        "*"  # Allow all origins for deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "PolyAgent Web API is running"}

# Quick test endpoint for polymarket connection
@app.get("/api/test")
async def test_services():
    from core.dependencies import get_polymarket_service
    try:
        polymarket_service = get_polymarket_service()
        # Simple test - don't actually call the API, just check if service exists
        return {"status": "ok", "polymarket_service": "initialized", "wallet": polymarket_service.polymarket.wallet_address}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Include routers
app.include_router(markets_router, prefix="/api/markets", tags=["Markets"])
app.include_router(trading_router, prefix="/api/trading", tags=["Trading"])
app.include_router(news_router, prefix="/api/news", tags=["News"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_markets":
                await websocket_manager.subscribe_to_markets(websocket)
            elif message.get("type") == "subscribe_news":
                await websocket_manager.subscribe_to_news(websocket)
            elif message.get("type") == "get_ai_analysis":
                await websocket_manager.get_ai_analysis(websocket, message.get("market_id"))
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "polymarket": polymarket_service is not None,
            "trading": trading_service is not None,
            "news": news_service is not None,
            "ai": ai_service is not None
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "PolyMastercould - AI-powered prediction market trading platform"}

# Dependency injection is now handled by core/dependencies.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)