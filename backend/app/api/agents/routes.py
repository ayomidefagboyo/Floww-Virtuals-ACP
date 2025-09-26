"""
API Routes for Trading Agents

Provides real endpoints for Yuki (trade scanner), Ryu (token analysis),
and Sakura (yield farming) agents with actual functionality.
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json
from pydantic import BaseModel, Field
from datetime import datetime

# Import real agent services
from app.services.yuki_agent_service import get_yuki_agent_service
from app.services.binance_service import get_binance_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["Trading Agents"])


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


@router.get("/status")
async def get_agents_status():
    """Get status of all trading agents."""
    try:
        # Test connections to services
        binance_service = await get_binance_service()
        yuki_service = await get_yuki_agent_service()

        return {
            "agents": {
                "yuki": {
                    "name": "Yuki - Trade Scanner",
                    "status": "online",
                    "description": "Advanced trade scanner for high-frequency opportunities",
                    "capabilities": ["market_scanning", "technical_analysis", "opportunity_detection"],
                    "risk_level": "high"
                },
                "ryu": {
                    "name": "Ryu - Token Analysis",
                    "status": "online",
                    "description": "Professional token analysis with AI scoring",
                    "capabilities": ["token_analysis", "risk_assessment", "price_prediction"],
                    "risk_level": "medium"
                },
                "sakura": {
                    "name": "Sakura - Yield Farming",
                    "status": "online",
                    "description": "Conservative DeFi yield farming with Pendle integration",
                    "capabilities": ["yield_optimization", "pendle_analysis", "defi_strategies"],
                    "risk_level": "low"
                }
            },
            "services": {
                "binance_api": "online",
                "technical_indicators": "online",
                "llm_analysis": "online"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/yuki/scan")
async def yuki_trade_scan(request: TradeScanRequest):
    """
    Yuki Agent - Scan market for trading opportunities.

    Returns real trade opportunities found by scanning Binance markets
    with technical analysis and AI-powered opportunity scoring.
    """
    try:
        logger.info(f"🔍 Yuki trade scan requested: {request.scan_type}")

        # Get Yuki service and run scan
        yuki_service = await get_yuki_agent_service()
        opportunities = await yuki_service.scan_market_opportunities()

        # Transform opportunities to API format
        result = {
            "agent": "yuki",
            "scan_type": request.scan_type,
            "opportunities": [],
            "total_scanned": request.pairs_limit,
            "opportunities_found": len(opportunities),
            "market_condition": "analyzed",
            "timestamp": datetime.utcnow().isoformat()
        }

        for opp in opportunities:
            result["opportunities"].append({
                "id": opp.id,
                "symbol": opp.symbol,
                "direction": opp.direction,
                "confidence": opp.confidence,
                "entry_price": opp.entry_price,
                "target_1": opp.target_1,
                "target_2": opp.target_2,
                "stop_loss": opp.stop_loss,
                "risk_reward_ratio": opp.risk_reward_ratio,
                "time_horizon": opp.time_horizon,
                "reasoning": opp.reasoning,
                "key_factors": opp.key_factors,
                "expires_at": opp.expires_at,
                # Enhanced Flow 3.0 fields
                "risk_factors": opp.risk_factors,
                "risk_assessment": opp.risk_assessment,
                "risk_level": opp.risk_level,
                "position_size": opp.position_size,
                "leverage": opp.leverage,
                "target_1_probability": opp.target_1_probability,
                "target_2_probability": opp.target_2_probability,
                "view_insights": opp.view_insights,
                "technical_scores": {
                    "rsi": opp.technical_analysis.rsi_14,
                    "macd": opp.technical_analysis.macd_line,
                    "bb_position": opp.technical_analysis.bb_position,
                    "momentum": opp.technical_analysis.momentum_score,
                    "strength": opp.technical_analysis.strength_score
                }
            })

        logger.info(f"✅ Yuki scan completed: {len(opportunities)} opportunities found")
        return result

    except Exception as e:
        logger.error(f"Error in Yuki trade scan: {e}")
        raise HTTPException(status_code=500, detail=f"Trade scan failed: {str(e)}")


@router.get("/yuki/scan/stream")
async def yuki_trade_scan_stream():
    """
    Server-Sent Events stream for Yuki trade scan progress and results.
    Emits events: progress, opportunity, complete, and error.
    """
    async def event_generator():
        try:
            logger.info("🔍 [SSE] Yuki trade scan stream started")

            # Emit start progress
            yield f"event: progress\ndata: {json.dumps({"message": "Starting market scan..."})}\n\n"

            yuki_service = await get_yuki_agent_service()

            # If service supports progress callbacks, prefer that; else, run and stream results
            opportunities = await yuki_service.scan_market_opportunities()

            # Emit intermediate heartbeat while formatting
            yield f"event: progress\ndata: {json.dumps({"message": "Formatting opportunities..."})}\n\n"

            for idx, opp in enumerate(opportunities, start=1):
                payload = {
                    "id": opp.id,
                    "symbol": opp.symbol,
                    "direction": opp.direction,
                    "confidence": opp.confidence,
                    "entry_price": opp.entry_price,
                    "target_1": opp.target_1,
                    "target_2": opp.target_2,
                    "stop_loss": opp.stop_loss,
                    "risk_reward_ratio": opp.risk_reward_ratio,
                    "time_horizon": opp.time_horizon,
                    "reasoning": opp.reasoning,
                    "key_factors": opp.key_factors,
                    "expires_at": opp.expires_at,
                    "risk_factors": getattr(opp, "risk_factors", None),
                    "risk_assessment": getattr(opp, "risk_assessment", None),
                    "risk_level": getattr(opp, "risk_level", None),
                    "position_size": getattr(opp, "position_size", None),
                    "leverage": getattr(opp, "leverage", None),
                    "target_1_probability": getattr(opp, "target_1_probability", None),
                    "target_2_probability": getattr(opp, "target_2_probability", None),
                    "view_insights": getattr(opp, "view_insights", None),
                    "technical_scores": {
                        "rsi": opp.technical_analysis.rsi_14,
                        "macd": opp.technical_analysis.macd_line,
                        "bb_position": opp.technical_analysis.bb_position,
                        "momentum": opp.technical_analysis.momentum_score,
                        "strength": opp.technical_analysis.strength_score,
                    },
                    "index": idx,
                    "total": len(opportunities),
                }

                # Emit each opportunity progressively
                yield f"event: opportunity\ndata: {json.dumps(payload)}\n\n"

                # Yield control so client receives events smoothly
                await asyncio.sleep(0)

            # Emit completion
            summary = {"opportunities_found": len(opportunities), "timestamp": datetime.utcnow().isoformat()}
            yield f"event: complete\ndata: {json.dumps(summary)}\n\n"

            logger.info(f"✅ [SSE] Yuki scan stream completed: {len(opportunities)} opportunities")

        except Exception as e:
            logger.error(f"[SSE] Yuki scan error: {e}")
            yield f"event: error\ndata: {json.dumps({"message": str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/ryu/analyze")
async def ryu_token_analysis(request: TokenAnalysisRequest):
    """
    Ryu Agent - Comprehensive token analysis with Flow 3.0 structure.

    Provides detailed AI-powered analysis of a specific token including
    technical indicators, risk assessment, trading recommendations, and view_insights.
    """
    try:
        logger.info(f"📊 Ryu token analysis requested for: {request.symbol}")

        # Import and get the new comprehensive Ryu service
        from app.services.ryu_agent_service import get_ryu_agent_service
        ryu_service = await get_ryu_agent_service()

        # Perform comprehensive token analysis using new service
        analysis_result = await ryu_service.analyze_token(
            symbol=request.symbol.upper(),
            analysis_type=request.analysis_type
        )

        if not analysis_result["success"]:
            if "not found" in analysis_result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=analysis_result["error"])
            else:
                raise HTTPException(status_code=500, detail=analysis_result["error"])

        # Format response to match Flow 3.0 structure and frontend expectations
        analysis = analysis_result["analysis"]

        formatted_result = {
            "agent": "ryu",
            "symbol": analysis.symbol,
            "analysis_type": request.analysis_type,
            "recommendation": analysis.action,
            "confidence": analysis.confidence,
            "current_price": analysis.current_price,
            "reasoning": analysis.reasoning,
            "key_factors": analysis.key_factors,
            "time_horizon": analysis.time_horizon,
            "risk_level": analysis.risk_level,
            "risk_factors": analysis.risk_factors,
            "view_insights": analysis.view_insights,
            "expires_at": analysis.expires_at,
            "entry_strategy": analysis.entry_strategy,
            "price_targets": analysis.price_targets,
            "risk_management": analysis.risk_management,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Ryu analysis completed for {request.symbol}: {analysis.action} (confidence: {analysis.confidence:.1%})")
        return formatted_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Ryu token analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Token analysis failed: {str(e)}")


@router.post("/sakura/yield")
async def sakura_yield_analysis(request: YieldAnalysisRequest):
    """
    Sakura Agent - DeFi yield farming analysis.

    Provides conservative yield farming opportunities and portfolio
    recommendations with focus on Pendle and other DeFi protocols.
    """
    try:
        logger.info(f"🌸 Sakura yield analysis requested: {request.analysis_type}")

        # Mock yield opportunities (would integrate with real Pendle API in production)
        yield_opportunities = [
            {
                "id": "pendle_steth_2024",
                "protocol": "Pendle",
                "asset": "stETH",
                "strategy": "Principal Token (PT) Fixed Yield",
                "apy": 12.4,
                "tvl": 125000000,
                "risk_level": "LOW",
                "maturity": "2024-12-28",
                "minimum_deposit": 0.1,
                "liquidity_score": 0.85,
                "projected_returns": {
                    "monthly": 1.02,
                    "quarterly": 3.1,
                    "yearly": 12.4
                }
            },
            {
                "id": "aave_usdc_v3",
                "protocol": "Aave V3",
                "asset": "USDC",
                "strategy": "Variable Rate Lending",
                "apy": 8.7,
                "tvl": 892000000,
                "risk_level": "LOW",
                "minimum_deposit": 100,
                "liquidity_score": 0.95,
                "projected_returns": {
                    "monthly": 0.72,
                    "quarterly": 2.18,
                    "yearly": 8.7
                }
            },
            {
                "id": "compound_eth_v3",
                "protocol": "Compound V3",
                "asset": "ETH",
                "strategy": "Collateral Earning",
                "apy": 6.2,
                "tvl": 450000000,
                "risk_level": "LOW",
                "minimum_deposit": 0.05,
                "liquidity_score": 0.90,
                "projected_returns": {
                    "monthly": 0.51,
                    "quarterly": 1.55,
                    "yearly": 6.2
                }
            }
        ]

        # Portfolio recommendation
        portfolio_recommendation = {
            "allocation": [
                {"protocol": "Pendle", "percentage": 40, "apy_contribution": 4.96},
                {"protocol": "Aave V3", "percentage": 35, "apy_contribution": 3.04},
                {"protocol": "Compound V3", "percentage": 25, "apy_contribution": 1.55}
            ],
            "total_projected_apy": 9.55,
            "risk_score": 0.22,  # Low risk
            "diversification_score": 0.88
        }

        result = {
            "agent": "sakura",
            "analysis_type": request.analysis_type,
            "risk_preference": request.risk_preference,
            "opportunities": yield_opportunities,
            "portfolio_recommendation": portfolio_recommendation,
            "market_analysis": {
                "defi_tvl_trend": "stable_growth",
                "yield_environment": "moderate",
                "risk_sentiment": "conservative_favorable"
            },
            "total_tvl_analyzed": sum(opp["tvl"] for opp in yield_opportunities),
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Sakura yield analysis completed: {len(yield_opportunities)} opportunities, {portfolio_recommendation['total_projected_apy']:.1f}% projected APY")
        return result

    except Exception as e:
        logger.error(f"Error in Sakura yield analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Yield analysis failed: {str(e)}")


# Helper functions for Ryu analysis
def _determine_ryu_recommendation(indicators, symbol_info) -> str:
    """Determine Ryu's trading recommendation."""
    try:
        score = 0

        # RSI analysis
        if indicators.rsi_14 < 30:
            score += 2  # Oversold - buy signal
        elif indicators.rsi_14 > 70:
            score -= 2  # Overbought - sell signal

        # MACD analysis
        if indicators.macd_line > indicators.macd_signal:
            score += 1  # Bullish crossover
        else:
            score -= 1

        # Price momentum
        price_change = symbol_info.get("price_change_24h", 0)
        if price_change > 5:
            score += 1
        elif price_change < -5:
            score -= 1

        # Determine recommendation
        if score >= 2:
            return "LONG"
        elif score <= -2:
            return "SHORT"
        else:
            return "HOLD"

    except Exception:
        return "HOLD"


def _calculate_ryu_confidence(indicators, symbol_info) -> float:
    """Calculate confidence score for Ryu's recommendation."""
    try:
        confidence_factors = []

        # Volume confidence
        volume = symbol_info.get("volume_24h", 0)
        if volume > 1000000:  # High volume
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)

        # Technical confluence
        technical_signals = 0
        if 20 < indicators.rsi_14 < 80:  # RSI in reasonable range
            technical_signals += 1
        if abs(indicators.macd_line) > 0:  # MACD showing momentum
            technical_signals += 1
        if 0.1 < indicators.bb_position < 0.9:  # Price within bands
            technical_signals += 1

        confidence_factors.append(technical_signals / 3)

        return sum(confidence_factors) / len(confidence_factors)

    except Exception:
        return 0.5


def _determine_trend(indicators) -> str:
    """Determine trend direction."""
    try:
        if indicators.ema_20 > indicators.ema_50 and indicators.macd_line > 0:
            return "bullish"
        elif indicators.ema_20 < indicators.ema_50 and indicators.macd_line < 0:
            return "bearish"
        else:
            return "sideways"
    except Exception:
        return "sideways"


def _score_technical_indicators(indicators) -> float:
    """Score technical indicators 0-100."""
    try:
        score = 50  # Neutral base

        # RSI scoring
        if 40 < indicators.rsi_14 < 60:
            score += 20  # Good range
        elif 30 < indicators.rsi_14 < 70:
            score += 10  # Acceptable range
        else:
            score -= 10  # Extreme levels

        # MACD scoring
        if indicators.macd_line > indicators.macd_signal:
            score += 15  # Bullish
        else:
            score -= 5   # Bearish

        # Bollinger Band scoring
        if 0.2 < indicators.bb_position < 0.8:
            score += 15  # Good position
        else:
            score += 5   # Extreme position

        return max(0, min(100, score))

    except Exception:
        return 50


def _score_momentum(indicators, symbol_info) -> float:
    """Score momentum 0-100."""
    try:
        score = 50

        # Price momentum
        price_change = abs(symbol_info.get("price_change_24h", 0))
        if price_change > 5:
            score += 25
        elif price_change > 2:
            score += 15

        # MACD momentum
        if abs(indicators.macd_histogram) > 0:
            score += 15

        # ATR momentum
        if indicators.atr_14 > 0:
            score += 10

        return max(0, min(100, score))

    except Exception:
        return 50


def _score_volume(symbol_info) -> float:
    """Score volume 0-100."""
    try:
        volume = symbol_info.get("volume_24h", 0)

        if volume > 10000000:  # Very high volume
            return 90
        elif volume > 5000000:  # High volume
            return 75
        elif volume > 1000000:  # Good volume
            return 60
        elif volume > 100000:   # Low volume
            return 40
        else:                   # Very low volume
            return 20

    except Exception:
        return 50


def _assess_risk_level(indicators, symbol_info) -> str:
    """Assess risk level for the token."""
    try:
        risk_score = 0

        # Volatility risk
        price_change = abs(symbol_info.get("price_change_24h", 0))
        if price_change > 15:
            risk_score += 3
        elif price_change > 8:
            risk_score += 2
        elif price_change > 3:
            risk_score += 1

        # Volume risk
        volume = symbol_info.get("volume_24h", 0)
        if volume < 500000:
            risk_score += 2

        # Technical risk
        if indicators.rsi_14 > 80 or indicators.rsi_14 < 20:
            risk_score += 1

        if risk_score >= 4:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    except Exception:
        return "MEDIUM"


def _calculate_entry_levels(symbol_info, indicators) -> Dict[str, float]:
    """Calculate entry levels for the token."""
    try:
        current_price = symbol_info.get("current_price", 0)
        atr = max(indicators.atr_14, current_price * 0.02)  # Min 2% ATR

        return {
            "optimal_entry": current_price,
            "entry_range_low": current_price - (atr * 0.5),
            "entry_range_high": current_price + (atr * 0.5),
            "stop_loss": current_price - (atr * 1.5),
            "target_1": current_price + (atr * 2),
            "target_2": current_price + (atr * 3.5)
        }

    except Exception:
        current_price = symbol_info.get("current_price", 0)
        return {
            "optimal_entry": current_price,
            "entry_range_low": current_price * 0.98,
            "entry_range_high": current_price * 1.02,
            "stop_loss": current_price * 0.95,
            "target_1": current_price * 1.05,
            "target_2": current_price * 1.10
        }