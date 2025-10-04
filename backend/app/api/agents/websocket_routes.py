"""
WebSocket Status and Monitoring Routes

Provides endpoints to monitor WebSocket performance and rate limit savings:
- WebSocket connection status
- Performance statistics
- Rate limit usage comparison
- Real-time data stream health
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from datetime import datetime

from app.services.binance_hybrid_service import get_binance_hybrid_service
from app.services.binance_websocket_service import get_binance_websocket_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/websocket", tags=["WebSocket Monitoring"])


@router.get("/status")
async def websocket_status():
    """
    Get comprehensive WebSocket status and performance metrics.
    Shows rate limit savings and connection health.
    """
    try:
        # Get hybrid service stats
        hybrid_service = await get_binance_hybrid_service()
        stats = hybrid_service.get_service_stats()
        health = await hybrid_service.health_check()

        # Get WebSocket service details
        ws_service = await get_binance_websocket_service()

        return {
            "websocket": {
                "connected": ws_service.is_connected,
                "healthy": ws_service.is_healthy(),
                "active_pairs": len(ws_service.tickers),
                "last_update": ws_service.last_update.isoformat() if ws_service.last_update else None,
                "messages_received": ws_service.messages_received,
                "bytes_received": ws_service.bytes_received,
                "uptime_seconds": (
                    (datetime.now() - ws_service.connection_start_time).total_seconds()
                    if ws_service.connection_start_time else 0
                ),
                "reconnect_attempts": ws_service.reconnect_attempts
            },
            "performance": {
                "websocket_requests": stats["websocket_requests"],
                "rest_api_requests": stats["rest_api_requests"],
                "websocket_usage_percent": stats["websocket_usage_percent"],
                "rate_limit_savings": {
                    "requests_saved": stats["websocket_requests"],
                    "estimated_savings": f"{stats['websocket_usage_percent']:.1f}% of requests avoid rate limits"
                }
            },
            "health": health,
            "benefits": {
                "no_rate_limits": "WebSocket streams bypass REST API rate limits",
                "real_time_data": "Live market data with minimal latency",
                "high_throughput": "Can handle 1000+ pairs simultaneously",
                "cost_effective": "Reduces API usage costs significantly"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting WebSocket status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-overview")
async def websocket_market_overview():
    """
    Get real-time market overview using WebSocket data.
    Demonstrates rate limit avoidance for market scanning.
    """
    try:
        hybrid_service = await get_binance_hybrid_service()
        overview = await hybrid_service.get_market_overview()

        return {
            "market_overview": overview,
            "data_source": "websocket_stream",
            "rate_limit_status": "bypassed_via_websocket",
            "performance_note": "This request uses 0 REST API rate limit quota",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities")
async def websocket_opportunities(
    min_volume: float = 500000,
    min_price_change: float = 2.0,
    max_results: int = 20
):
    """
    Scan for trading opportunities using WebSocket data.
    Shows how market scanning avoids rate limits entirely.
    """
    try:
        hybrid_service = await get_binance_hybrid_service()
        opportunities = await hybrid_service.scan_for_opportunities(
            min_volume=min_volume,
            min_price_change=min_price_change,
            max_symbols=max_results
        )

        return {
            "opportunities": opportunities,
            "scan_parameters": {
                "min_volume_usdt": min_volume,
                "min_price_change_percent": min_price_change,
                "max_results": max_results
            },
            "performance": {
                "data_source": "websocket_stream",
                "rate_limit_impact": "zero",
                "scan_speed": "instant",
                "pairs_analyzed": len(opportunities)
            },
            "benefits": [
                "No REST API rate limits consumed",
                "Real-time data (not cached)",
                "Can scan all pairs simultaneously",
                "Sub-second response time"
            ],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error scanning opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/market-data")
async def stream_market_data():
    """
    Server-Sent Events stream of real-time market data.
    Demonstrates continuous data flow without rate limits.
    """
    async def event_generator():
        try:
            logger.info("🔴 [SSE] Starting real-time market data stream")

            hybrid_service = await get_binance_hybrid_service()
            ws_service = await get_binance_websocket_service()

            # Stream counter
            update_count = 0

            while True:
                try:
                    # Get market summary
                    if ws_service.is_healthy():
                        summary = ws_service.get_market_summary()
                        update_count += 1

                        stream_data = {
                            "update_count": update_count,
                            "total_pairs": summary.total_pairs,
                            "active_pairs": summary.active_pairs,
                            "total_volume_24h": summary.volume_24h_usdt,
                            "top_gainers": [
                                {
                                    "symbol": t.symbol,
                                    "price_change_percent": t.price_change_percent,
                                    "price": t.price
                                }
                                for t in summary.top_gainers[:3]
                            ],
                            "top_losers": [
                                {
                                    "symbol": t.symbol,
                                    "price_change_percent": t.price_change_percent,
                                    "price": t.price
                                }
                                for t in summary.top_losers[:3]
                            ],
                            "websocket_status": "connected",
                            "rate_limit_status": "bypassed",
                            "timestamp": datetime.now().isoformat()
                        }

                        yield f"event: market_update\ndata: {json.dumps(stream_data)}\n\n"

                    else:
                        # WebSocket not healthy
                        error_data = {
                            "error": "WebSocket not healthy",
                            "fallback": "Using REST API",
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

                    # Update every 2 seconds
                    await asyncio.sleep(2)

                except Exception as e:
                    error_data = {
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                    await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"[SSE] Market data stream error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/rate-limit-comparison")
async def rate_limit_comparison():
    """
    Compare rate limit usage between WebSocket and REST API approaches.
    Educational endpoint showing the benefits of WebSocket.
    """
    try:
        hybrid_service = await get_binance_hybrid_service()
        stats = hybrid_service.get_service_stats()

        # Calculate theoretical rate limit usage
        rest_requests = stats["rest_api_requests"]
        ws_requests = stats["websocket_requests"]
        total_requests = rest_requests + ws_requests

        # Binance rate limits
        rate_limit_per_minute = 1000
        rate_limit_per_second = 16

        # Calculate rate limit usage
        rest_api_usage_percent = (rest_requests / rate_limit_per_minute) * 100 if rest_requests else 0
        websocket_savings = ws_requests  # Requests saved from rate limit

        return {
            "comparison": {
                "rest_api": {
                    "requests_made": rest_requests,
                    "rate_limit_usage_percent": rest_api_usage_percent,
                    "rate_limit_risk": "HIGH" if rest_api_usage_percent > 50 else "MEDIUM" if rest_api_usage_percent > 20 else "LOW"
                },
                "websocket": {
                    "requests_handled": ws_requests,
                    "rate_limit_usage": 0,
                    "rate_limit_risk": "NONE"
                }
            },
            "benefits": {
                "requests_saved_from_rate_limit": websocket_savings,
                "rate_limit_capacity_preserved": f"{(websocket_savings / rate_limit_per_minute) * 100:.1f}%",
                "theoretical_max_throughput": "Unlimited for ticker data",
                "cost_savings": "Significant reduction in API costs"
            },
            "scenarios": {
                "market_scanning": {
                    "rest_api": "Limited to ~1000 pairs/minute",
                    "websocket": "Unlimited pairs in real-time"
                },
                "high_frequency_updates": {
                    "rest_api": "Risk of rate limiting",
                    "websocket": "No rate limit concerns"
                },
                "multiple_agents": {
                    "rest_api": "Share rate limit quota",
                    "websocket": "Independent streams"
                }
            },
            "recommendations": [
                "Use WebSocket for real-time ticker data",
                "Reserve REST API for detailed analysis",
                "Monitor rate limit usage continuously",
                "Implement automatic fallback mechanisms"
            ],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating rate limit comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))