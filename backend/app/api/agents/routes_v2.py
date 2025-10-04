"""
Agent API Routes v2 - Reliable Agent System

Provides reliable API endpoints for all trading agents with:
- Guaranteed response format
- Comprehensive error handling
- Fallback mechanisms
- Consistent status reporting
"""

import asyncio
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel, Field
from datetime import datetime

# Import reliable agents
from app.services.ryu_agent_v2 import get_ryu_agent
from app.services.yuki_agent_v2 import get_yuki_agent
from app.services.sakura_agent_v2 import get_sakura_agent
from app.services.usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["Trading Agents v2"])


# Request Models
class TokenAnalysisRequest(BaseModel):
    """Request for token analysis."""
    symbol: str = Field(..., description="Token symbol (e.g., BTC, ETH)")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")


class TradeScanRequest(BaseModel):
    """Request for trade scanning."""
    scan_type: str = Field(default="opportunities", description="Type of scan")
    pairs_limit: int = Field(default=500, description="Maximum pairs to scan")


class YieldAnalysisRequest(BaseModel):
    """Request for yield analysis."""
    analysis_type: str = Field(default="yield_farming", description="Type of yield analysis")
    risk_preference: str = Field(default="conservative", description="Risk preference")
    investment_amount: float = Field(default=10000, description="Investment amount in USD", ge=0)


# Usage endpoint
@router.get("/usage")
async def get_usage_info(request: Request):
    """Get current usage information for all agents."""
    try:
        client_ip = request.client.host
        usage_info = usage_tracker.get_all_usage(client_ip)
        
        return {
            "user_ip": client_ip,
            "daily_limit": 3,
            "usage": usage_info,
            "reset_time": usage_tracker._get_reset_time()
        }
    except Exception as e:
        logger.error(f"Error getting usage info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Status endpoint
@router.get("/status")
async def get_agents_status():
    """Get comprehensive status of all trading agents."""
    try:
        # Get agent instances
        ryu_agent = await get_ryu_agent()
        yuki_agent = await get_yuki_agent()
        sakura_agent = await get_sakura_agent()

        # Get individual statuses
        agents_status = {
            "ryu": ryu_agent.get_status(),
            "yuki": yuki_agent.get_status(),
            "sakura": sakura_agent.get_status()
        }

        # Overall system status
        all_online = all(
            agent_status['status'] == 'online'
            for agent_status in agents_status.values()
        )

        return {
            "agents": {
                "ryu": {
                    "name": "Ryu Agent",
                    "status": agents_status["ryu"]["status"],
                    "description": "Comprehensive token analysis with technical indicators",
                    "capabilities": agents_status["ryu"]["capabilities"],
                    "risk_level": "medium",
                    "last_activity": agents_status["ryu"]["last_activity"]
                },
                "yuki": {
                    "name": "Yuki Agent",
                    "status": agents_status["yuki"]["status"],
                    "description": "Real-time market scanning for trading opportunities",
                    "capabilities": agents_status["yuki"]["capabilities"],
                    "risk_level": "high",
                    "last_activity": agents_status["yuki"]["last_activity"]
                },
                "sakura": {
                    "name": "Sakura Agent",
                    "status": agents_status["sakura"]["status"],
                    "description": "Conservative DeFi yield farming analysis",
                    "capabilities": agents_status["sakura"]["capabilities"],
                    "risk_level": "low",
                    "last_activity": agents_status["sakura"]["last_activity"]
                }
            },
            "system": {
                "status": "online" if all_online else "partial",
                "version": "2.0",
                "reliability": "high",
                "fallback_enabled": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ryu Agent - Token Analysis
@router.post("/ryu/analyze")
async def ryu_token_analysis(request: TokenAnalysisRequest, http_request: Request):
    """
    Ryu Agent - Comprehensive token analysis with guaranteed response.

    Provides detailed analysis including technical indicators,
    risk assessment, and trading recommendations.
    """
    # Check rate limit first (outside try block)
    client_ip = http_request.client.host
    can_request, usage_info = usage_tracker.can_make_request(client_ip, "ryu")
    
    if not can_request:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "You've reached the daily limit of 3 requests for Ryu Agent. Please try again tomorrow.",
                "usage_info": usage_info
            }
        )

    try:
        
        logger.info(f"🎯 Ryu token analysis requested for: {request.symbol}")

        # Get Ryu agent
        ryu_agent = await get_ryu_agent()

        # Execute analysis
        result = await ryu_agent.execute({
            "symbol": request.symbol,
            "analysis_type": request.analysis_type
        })

        # Format response
        if result.success:
            # Record successful usage
            usage_tracker.record_request(client_ip, "ryu")
            
            analysis_data = result.data
            response = {
                "agent": "ryu",
                "symbol": analysis_data["symbol"],
                "analysis_type": request.analysis_type,
                "recommendation": analysis_data["action"],
                "confidence": analysis_data["confidence"],
                "current_price": analysis_data["current_price"],
                "reasoning": analysis_data["reasoning"],
                "key_factors": analysis_data["key_factors"],
                "time_horizon": analysis_data["time_horizon"],
                "risk_level": analysis_data["risk_level"],
                "entry_strategy": analysis_data["entry_strategy"],
                "price_targets": analysis_data["price_targets"],
                "technical_analysis": analysis_data["technical_analysis"],
                "market_data": analysis_data["market_data"],
                "expires_at": analysis_data["expires_at"],
                "timestamp": result.timestamp,
                "status": "success"
            }
        else:
            # Error response
            response = {
                "agent": "ryu",
                "symbol": request.symbol,
                "error": result.error,
                "status": "error",
                "timestamp": result.timestamp,
                "fallback_available": True
            }

        logger.info(f"✅ Ryu analysis completed for {request.symbol}")
        return response

    except Exception as e:
        logger.error(f"Error in Ryu token analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Token analysis failed: {str(e)}")


# Yuki Agent - Market Scanner
@router.post("/yuki/scan")
async def yuki_trade_scan(request: TradeScanRequest, http_request: Request):
    """
    Yuki Agent - Market scanning for trading opportunities.

    Scans cryptocurrency markets and returns high-confidence
    trading opportunities with technical analysis.
    """
    # Check rate limit first (outside try block)
    client_ip = http_request.client.host
    can_request, usage_info = usage_tracker.can_make_request(client_ip, "yuki")
    
    if not can_request:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "You've reached the daily limit of 3 requests for Yuki Agent. Please try again tomorrow.",
                "usage_info": usage_info
            }
        )

    try:
        
        logger.info(f"🔍 Yuki trade scan requested: {request.scan_type}")

        # Get Yuki agent
        yuki_agent = await get_yuki_agent()

        # Execute scan
        result = await yuki_agent.execute({
            "scan_type": request.scan_type,
            "pairs_limit": request.pairs_limit
        })

        # Format response
        if result.success:
            # Record successful usage
            usage_tracker.record_request(client_ip, "yuki")
            
            scan_data = result.data
            response = {
                "agent": "yuki",
                "scan_type": request.scan_type,
                "opportunities": scan_data["opportunities"],
                "total_scanned": scan_data["total_scanned"],
                "candidates_analyzed": scan_data["candidates_analyzed"],
                "opportunities_found": len(scan_data["opportunities"]),
                "market_condition": scan_data["market_condition"],
                "timestamp": result.timestamp,
                "status": "success"
            }
        else:
            # Error response
            response = {
                "agent": "yuki",
                "scan_type": request.scan_type,
                "opportunities": [],
                "error": result.error,
                "status": "error",
                "timestamp": result.timestamp,
                "fallback_available": True
            }

        logger.info(f"✅ Yuki scan completed: {len(response.get('opportunities', []))} opportunities found")
        return response

    except Exception as e:
        logger.error(f"Error in Yuki trade scan: {e}")
        raise HTTPException(status_code=500, detail=f"Trade scan failed: {str(e)}")


# Yuki Agent - Streaming Scan
@router.get("/yuki/scan/stream")
async def yuki_trade_scan_stream():
    """
    Server-Sent Events stream for Yuki trade scan progress.
    Provides real-time updates during market scanning.
    """
    async def event_generator():
        try:
            logger.info("🔍 [SSE] Yuki trade scan stream started")

            # Emit start event
            yield f"event: progress\ndata: {json.dumps({'message': 'Starting market scan...'})}\n\n"

            # Get Yuki agent
            yuki_agent = await get_yuki_agent()

            # Execute scan with progress updates
            result = await yuki_agent.execute({
                "scan_type": "opportunities",
                "pairs_limit": 500
            })

            if result.success:
                scan_data = result.data
                opportunities = scan_data["opportunities"]

                # Emit opportunities one by one
                for idx, opportunity in enumerate(opportunities, 1):
                    opportunity_with_progress = {
                        **opportunity,
                        "index": idx,
                        "total": len(opportunities)
                    }
                    yield f"event: opportunity\ndata: {json.dumps(opportunity_with_progress)}\n\n"
                    await asyncio.sleep(0.1)  # Small delay for smooth streaming

                # Emit completion
                summary = {
                    "opportunities_found": len(opportunities),
                    "market_condition": scan_data["market_condition"],
                    "timestamp": result.timestamp
                }
                yield f"event: complete\ndata: {json.dumps(summary)}\n\n"

            else:
                # Emit error
                yield f"event: error\ndata: {json.dumps({'message': result.error})}\n\n"

            logger.info("✅ [SSE] Yuki scan stream completed")

        except Exception as e:
            logger.error(f"[SSE] Yuki scan error: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Sakura Agent - Yield Analysis
@router.post("/sakura/yield")
async def sakura_yield_analysis(request: YieldAnalysisRequest, http_request: Request):
    """
    Sakura Agent - DeFi yield farming analysis.

    Provides conservative yield farming opportunities with
    risk assessment and portfolio allocation recommendations.
    """
    # Check rate limit first (outside try block)
    client_ip = http_request.client.host
    can_request, usage_info = usage_tracker.can_make_request(client_ip, "sakura")
    
    if not can_request:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "You've reached the daily limit of 3 requests for Sakura Agent. Please try again tomorrow.",
                "usage_info": usage_info
            }
        )

    try:
        
        logger.info(f"🌸 Sakura yield analysis requested: {request.analysis_type}")

        # Import and get the real Sakura Pendle agent
        from app.services.sakura_agent_pendle import get_sakura_pendle_agent
        sakura_agent = await get_sakura_pendle_agent()

        # Execute real analysis with Pendle integration
        analysis_params = {
            "analysis_type": request.analysis_type,
            "risk_preference": request.risk_preference,
            "investment_amount": request.investment_amount
        }

        analysis_result = await sakura_agent._execute_analysis(analysis_params)

        # Record successful usage
        usage_tracker.record_request(client_ip, "sakura")

        # Format response to match API structure
        response = {
            "agent": "sakura",
            "analysis_type": request.analysis_type,
            "risk_preference": request.risk_preference,
            "opportunities": analysis_result.get("opportunities", []),
            "portfolio_allocation": analysis_result.get("portfolio_allocation", {}),
            "market_analysis": analysis_result.get("market_summary", {}),
            "risk_assessment": analysis_result.get("risk_assessment", {}),
            "total_tvl_analyzed": analysis_result.get("market_summary", {}).get("total_tvl_analyzed", 0),
            "timestamp": analysis_result.get("timestamp", datetime.utcnow().isoformat())
        }

        logger.info(f"✅ Sakura yield analysis completed: {len(response.get('opportunities', []))} opportunities found")
        return response

    except Exception as e:
        logger.error(f"Error in Sakura yield analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Yield analysis failed: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for agent system.
    """
    try:
        # Quick health check for all agents
        checks = {}

        try:
            ryu_agent = await get_ryu_agent()
            checks["ryu"] = ryu_agent.status.value
        except Exception as e:
            checks["ryu"] = f"error: {str(e)}"

        try:
            yuki_agent = await get_yuki_agent()
            checks["yuki"] = yuki_agent.status.value
        except Exception as e:
            checks["yuki"] = f"error: {str(e)}"

        try:
            sakura_agent = await get_sakura_agent()
            checks["sakura"] = sakura_agent.status.value
        except Exception as e:
            checks["sakura"] = f"error: {str(e)}"

        # Overall health
        healthy_agents = sum(1 for status in checks.values() if status == "online")
        overall_health = "healthy" if healthy_agents == 3 else "partial" if healthy_agents > 0 else "unhealthy"

        return {
            "status": overall_health,
            "agents": checks,
            "healthy_agents": healthy_agents,
            "total_agents": 3,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }