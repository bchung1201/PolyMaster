from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
import json

from services.ai_service import AIService
from api.v1.models.requests.base import (
    AIAnalysisRequest, 
    ChatRequest, 
    NewsImpactRequest, 
    MarketCategory
)
from api.v1.models.responses.base import (
    AIAnalysisResponse,
    ChatResponse,
    MarketRecommendationsResponse,
    NewsImpactResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Import dependency injection functions
from core.dependencies import get_ai_service, get_polymarket_service, get_news_service

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_market(
    analysis_request: AIAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get AI analysis for a market"""
    try:
        analysis = await ai_service.get_market_analysis(
            analysis_request.market_question,
            analysis_request.outcome
        )
        
        return AIAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Chat with AI assistant"""
    try:
        response = await ai_service.chat_with_ai(chat_request.message)
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations", response_model=MarketRecommendationsResponse)
async def get_market_recommendations(
    category: Optional[MarketCategory] = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get AI-recommended markets for trading"""
    try:
        recommendations = await ai_service.get_market_recommendations(
            category=category.value if category else None,
            limit=limit
        )
        
        return MarketRecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations),
            timestamp=recommendations[0].get("timestamp", "") if recommendations else ""
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news")
async def get_relevant_news(
    keywords: str = Query(..., description="Keywords to search for relevant news"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get relevant news articles for specific keywords (CLI method)"""
    try:
        result = await ai_service.get_relevant_news_for_keywords(keywords)
        return result
        
    except Exception as e:
        logger.error(f"Error getting relevant news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/markets/filtered")
async def get_filtered_markets(
    limit: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="spread", description="Sort by: spread, volume"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get filtered and sorted markets using CLI logic"""
    try:
        result = await ai_service.get_filtered_markets(limit=limit, sort_by=sort_by)
        return result
        
    except Exception as e:
        logger.error(f"Error getting filtered markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/filtered") 
async def get_filtered_events(
    limit: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="number_of_markets", description="Sort by: number_of_markets"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get filtered and sorted events using CLI logic"""
    try:
        result = await ai_service.get_filtered_events(limit=limit, sort_by=sort_by)
        return result
        
    except Exception as e:
        logger.error(f"Error getting filtered events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/superforecaster")
async def ask_superforecaster_detailed(
    event_title: str,
    market_question: str,
    outcome: str = "yes",
    ai_service: AIService = Depends(get_ai_service)
):
    """Enhanced superforecaster analysis (CLI method)"""
    try:
        result = await ai_service.ask_superforecaster_detailed(
            event_title=event_title,
            market_question=market_question, 
            outcome=outcome
        )
        return result
        
    except Exception as e:
        logger.error(f"Error in superforecaster analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights")
async def get_polymarket_insights(
    query: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get insights about Polymarket using RAG"""
    try:
        insights = await ai_service.get_polymarket_insights(query)
        return insights
        
    except Exception as e:
        logger.error(f"Error getting Polymarket insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/market-idea")
async def create_market_idea(
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate new market creation idea"""
    try:
        idea = await ai_service.create_market_idea()
        return idea
        
    except Exception as e:
        logger.error(f"Error creating market idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/news-impact", response_model=NewsImpactResponse)
async def analyze_news_impact(
    impact_request: NewsImpactRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Analyze how news articles might impact a market"""
    try:
        impact = await ai_service.analyze_news_impact(
            impact_request.news_articles,
            impact_request.market_question
        )
        
        return NewsImpactResponse(**impact)
        
    except Exception as e:
        logger.error(f"Error analyzing news impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream-analysis/{market_question}")
async def stream_market_analysis(
    market_question: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Stream AI analysis as it's generated"""
    try:
        async def generate_analysis():
            async for chunk in ai_service.stream_analysis(market_question):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            generate_analysis(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Error streaming analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coach/{market_id}")
async def get_ai_coach_analysis(
    market_id: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get comprehensive AI coach analysis for a market"""
    try:
        # Get market data
        polymarket_service = get_polymarket_service()
        news_service = get_news_service()
        
        market_data = await polymarket_service.get_market_by_id(market_id)
        
        # Get related news
        news_data = await news_service.get_market_news(
            market_data["question"], 
            limit=10
        )
        
        # Get AI analysis
        analysis = await ai_service.get_market_analysis(market_data["question"])
        
        # Get news impact
        news_impact = await ai_service.analyze_news_impact(
            news_data, 
            market_data["question"]
        )
        
        # Get trading strategy
        strategy = await ai_service.get_trading_strategy(market_data, news_data)
        
        return {
            "market_id": market_id,
            "market_data": market_data,
            "analysis": analysis,
            "news_impact": news_impact,
            "strategy": strategy,
            "related_news": news_data[:5],  # Top 5 most relevant
            "timestamp": analysis.get("timestamp", "")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting AI coach analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trading-analysis")
async def get_trading_bot_analysis(
    ai_service: AIService = Depends(get_ai_service)
):
    """Get comprehensive trading bot analysis for AI coach (demo mode - no actual trades)"""
    try:
        from core.dependencies import get_trading_service
        trading_service = get_trading_service()
        
        # Run autonomous trading analysis in demo mode
        result = await trading_service.run_autonomous_trading(dry_run=True)
        
        if result and result.get("trade_decision"):
            trade_decision = result["trade_decision"]
            
            # Format the analysis for the AI coach
            formatted_analysis = f"""
**🤖 Trading Bot Analysis**

**Market:** {trade_decision.get('market_question', 'N/A')}

**Recommendation:** {trade_decision.get('action', 'N/A')}
**Target Price:** ${trade_decision.get('target_price', 0):.4f}
**Edge Detected:** {trade_decision.get('edge', 0):.2%}
**Confidence:** {trade_decision.get('confidence', 0):.0%}

**🧠 AI Reasoning:**
{trade_decision.get('reasoning', 'No reasoning provided')}

**📊 Detailed Analysis:**
{trade_decision.get('analysis', 'No detailed analysis available')}

---
*This is a demo analysis. No actual trades were executed.*
"""
            
            return {
                "success": True,
                "analysis": formatted_analysis,
                "trade_decision": trade_decision,
                "demo_mode": True,
                "timestamp": result.get("timestamp"),
                "type": "trading_analysis"
            }
        else:
            return {
                "success": False,
                "analysis": "No trading opportunities found at this time. The AI trading bot is continuously monitoring markets for profitable opportunities.",
                "demo_mode": True,
                "type": "trading_analysis"
            }
            
    except Exception as e:
        logger.error(f"Error getting trading bot analysis: {e}")
        return {
            "success": False,
            "analysis": f"Trading bot analysis temporarily unavailable: {str(e)}",
            "demo_mode": True,
            "type": "trading_analysis"
        }

# ===== NEW ENHANCED ENDPOINTS USING SPECIFIC PROMPTS =====

@router.post("/professional-analysis")
async def get_professional_market_analysis(
    analysis_request: AIAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Get professional market analysis using superforecaster prompt from prompts.py"""
    try:
        analysis = await ai_service.get_professional_market_analysis(
            analysis_request.market_question,
            analysis_request.outcome
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting professional market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news-sentiment")
async def get_news_with_sentiment(
    keywords: str = Query(..., description="Keywords for news search with sentiment analysis"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get relevant news with sentiment analysis using prompts.py"""
    try:
        result = await ai_service.get_news_with_sentiment(keywords)
        return result
        
    except Exception as e:
        logger.error(f"Error getting news with sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edge-calculation")
async def calculate_market_edge(
    analysis_request: AIAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Calculate trading edge using professional analysis from prompts.py"""
    try:
        edge_result = await ai_service.calculate_market_edge(
            analysis_request.market_question,
            analysis_request.outcome
        )
        
        return edge_result
        
    except Exception as e:
        logger.error(f"Error calculating market edge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-insights")
async def get_comprehensive_market_insights(
    market_question: str = Query(..., description="Market question for comprehensive insights"),
    ai_service: AIService = Depends(get_ai_service)
):
    """Get comprehensive market insights using Polymarket analyst prompts from prompts.py"""
    try:
        insights = await ai_service.get_comprehensive_market_insights(market_question)
        return insights
        
    except Exception as e:
        logger.error(f"Error getting comprehensive market insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))