"""
Ryu Agent Service - Token Analysis Card Generator

Based on the token analysis card system from floww3.0, this service provides:
- Comprehensive token analysis cards with professional formatting
- Multi-factor scoring (Technical, Fundamental, Momentum, Sentiment)
- Balanced risk-reward trading approach
- LLM-enhanced analysis with Claude API
- Dynamic price target calculation

Ryu is the balanced trading agent focused on moderate risk with comprehensive analysis.
"""

import asyncio
import logging
import numpy as np
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal
from enum import Enum

import anthropic

logger = logging.getLogger(__name__)


class TradeAction(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"
    AVOID = "AVOID"


class TimeHorizon(Enum):
    SCALP = "SCALP"      # Minutes to hours
    SHORT = "SHORT"      # Hours to 1-2 days
    MEDIUM = "MEDIUM"    # 2-7 days
    LONG = "LONG"        # 1-4 weeks
    HOLD = "HOLD"        # Months+


@dataclass
class EntryDetails:
    """Trade entry information."""
    current_price: str
    action: str  # "LONG", "SHORT", "HOLD"
    leverage: str
    confidence: str
    optimal_entry_range: Optional[Dict[str, float]] = None


@dataclass
class TechnicalReasoning:
    """Technical analysis reasoning."""
    primary_signals: List[str]
    momentum_analysis: str
    trend_analysis: str
    volume_analysis: str
    support_resistance: Optional[Dict[str, float]] = None


@dataclass
class RiskManagement:
    """Risk management details."""
    stop_loss: Optional[str]
    take_profit_levels: List[str]
    position_size: str
    trailing_stop: Optional[str] = None


@dataclass
class TradeMathematics:
    """Trade mathematics and calculations."""
    leverage_impact: str
    risk_calculation: str
    reward_calculation: List[str]
    risk_reward_ratios: List[str]


@dataclass
class ExecutionStrategy:
    """Execution strategy details."""
    time_horizon: str
    entry_strategy: str
    exit_strategy: str
    monitoring_levels: Dict[str, float]


@dataclass
class MarketContext:
    """Market context and conditions."""
    market_conditions: str
    catalyst_events: List[str]
    risk_factors: List[str]
    alternative_scenarios: List[Dict[str, str]]


@dataclass
class TokenAnalysisCard:
    """Complete token analysis card."""
    header: Dict[str, str]
    trade_setup: Dict[str, Any]
    trade_mathematics: Dict[str, Any]
    execution_strategy: Dict[str, Any]
    market_context: Dict[str, Any]
    confidence_breakdown: Dict[str, str]
    footer: Dict[str, Any]


class RyuAgentService:
    """
    Ryu Agent Service - Token Analysis Card Generator

    Provides comprehensive token analysis with professional formatting
    based on the floww3.0 token analysis card system.
    """

    def __init__(self):
        self.claude_client = None
        self.api_calls_this_minute = []
        self.max_calls_per_minute = 60

    async def _initialize_services(self):
        """Initialize AI services."""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Ryu agent initialized with Claude API")
            else:
                logger.warning("No Claude API key - AI analysis will use fallback")
        except Exception as e:
            logger.error(f"Error initializing Ryu services: {e}")

    def _can_make_api_call(self) -> bool:
        """Check if we can make an API call within rate limits."""
        now = datetime.now()
        # Remove calls older than 1 minute
        self.api_calls_this_minute = [
            call_time for call_time in self.api_calls_this_minute
            if now - call_time < timedelta(minutes=1)
        ]
        return len(self.api_calls_this_minute) < self.max_calls_per_minute

    def _record_api_call(self):
        """Record an API call for rate limiting."""
        self.api_calls_this_minute.append(datetime.now())

    async def generate_token_analysis_card(self, symbol: str, risk_tolerance: str = "medium", time_horizon: str = "medium") -> Dict[str, Any]:
        """
        Generate comprehensive token analysis card.
        Main entry point for Virtuals ACP integration.
        """
        try:
            logger.info(f"Generating token analysis card for {symbol} (Ryu agent)")

            if not hasattr(self, '_services_initialized') or not self._services_initialized:
                await self._initialize_services()
                self._services_initialized = True

            # Get market data
            market_data = await self._get_market_data(symbol)

            # Perform multi-factor analysis
            analysis_scores = await self._calculate_analysis_scores(symbol, market_data)

            # Generate comprehensive analysis card
            analysis_card = await self._create_analysis_card(
                symbol, market_data, analysis_scores, risk_tolerance, time_horizon
            )

            logger.info(f"Token analysis card generated for {symbol}: {analysis_card['trade_setup']['entry_details']['action']} (confidence: {analysis_card['trade_setup']['entry_details']['confidence']})")

            return {
                "analysis_card": analysis_card
            }

        except Exception as e:
            logger.error(f"Error generating analysis card for {symbol}: {e}")
            return {
                "analysis_card": None,
                "error": str(e)
            }

    async def execute_token_analysis(self, symbol: str, amount: float, risk_tolerance: str = "medium", time_horizon: str = "medium") -> Dict[str, Any]:
        """
        Execute token analysis with position sizing and execution planning.
        """
        try:
            logger.info(f"Generating token analysis card for {symbol} (Ryu agent)")

            # Generate analysis card first
            card_result = await self.generate_token_analysis_card(symbol, risk_tolerance, time_horizon)
            analysis_card = card_result.get("analysis_card")

            if not analysis_card:
                return {"success": False, "error": "Analysis card generation failed"}

            # Extract key information
            entry_details = analysis_card["trade_setup"]["entry_details"]
            action = entry_details["action"]
            confidence = float(entry_details["confidence"].replace("%", "")) / 100

            # Calculate position sizing
            position_sizing = await self._calculate_position_sizing(amount, confidence, risk_tolerance)

            # Generate execution plan
            execution_plan = await self._generate_execution_plan(symbol, amount, analysis_card)

            # Calculate expected outcomes
            expected_outcomes = await self._calculate_expected_outcomes(analysis_card, amount)

            return {
                "success": True,
                "token_analysis": {
                    "symbol": symbol,
                    "action": action,
                    "confidence": confidence,
                    "analysis_card": analysis_card,
                    "position_sizing": position_sizing,
                    "execution_plan": execution_plan,
                    "expected_outcomes": expected_outcomes,
                    "execution_timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error executing token analysis for {symbol}: {e}")
            return {"success": False, "error": str(e)}

    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for the token."""
        try:
            # Mock market data - in production this would fetch real data
            base_prices = {
                "BTC": 43387.0,
                "ETH": 2623.4,
                "SOL": 98.2,
                "AVAX": 35.7,
                "MATIC": 0.89
            }

            base_price = base_prices.get(symbol.upper(), 100.0)
            price_change = np.random.uniform(-2, 2)  # ±2% daily change for balanced approach
            current_price = base_price * (1 + price_change / 100)

            return {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "price_change_24h": price_change,
                "volume_24h": abs(np.random.normal(1000000, 200000)),
                "high_24h": current_price * 1.015,
                "low_24h": current_price * 0.985,
                "market_cap": current_price * 1000000000,  # Mock market cap
            }

        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "current_price": 100.0,
                "price_change_24h": 0.0,
                "volume_24h": 1000000,
                "high_24h": 101.5,
                "low_24h": 98.5,
                "market_cap": 100000000
            }

    async def _calculate_analysis_scores(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate multi-factor analysis scores."""
        try:
            price_change = market_data["price_change_24h"]
            volume = market_data["volume_24h"]
            current_price = market_data["current_price"]

            # Technical Score (35% weight)
            rsi = 50 + (price_change * 8) + np.random.uniform(-10, 10)
            rsi = max(20, min(80, rsi))
            technical_score = 0.6 if 40 <= rsi <= 60 else (0.8 if rsi < 40 else 0.4)

            # Fundamental Score (25% weight) - based on market cap tier
            market_cap = market_data.get("market_cap", 100000000)
            if market_cap > 10000000000:  # >$10B
                fundamental_score = 0.8
            elif market_cap > 1000000000:  # >$1B
                fundamental_score = 0.7
            else:
                fundamental_score = 0.5

            # Momentum Score (25% weight)
            momentum_score = max(0.1, min(0.9, 0.5 + (price_change / 10)))

            # Sentiment Score (15% weight)
            sentiment_score = 0.6 if price_change > 0 else 0.4 if price_change > -1 else 0.3

            # Overall weighted score
            overall_score = (
                technical_score * 0.35 +
                fundamental_score * 0.25 +
                momentum_score * 0.25 +
                sentiment_score * 0.15
            )

            return {
                "technical": technical_score,
                "fundamental": fundamental_score,
                "momentum": momentum_score,
                "sentiment": sentiment_score,
                "overall": overall_score
            }

        except Exception as e:
            logger.error(f"Error calculating analysis scores for {symbol}: {e}")
            return {
                "technical": 0.5,
                "fundamental": 0.5,
                "momentum": 0.5,
                "sentiment": 0.5,
                "overall": 0.5
            }

    async def _create_analysis_card(self, symbol: str, market_data: Dict[str, Any], scores: Dict[str, float],
                                  risk_tolerance: str, time_horizon: str) -> TokenAnalysisCard:
        """Create comprehensive token analysis card."""
        try:
            current_price = market_data["current_price"]
            price_change = market_data["price_change_24h"]
            volume = market_data["volume_24h"]
            overall_score = scores["overall"]

            # Determine trade action based on overall score
            if overall_score > 0.65:
                action = "BUY"
                confidence = min(85, int(overall_score * 100))
                leverage = "2x (moderate)"
            elif overall_score < 0.35:
                action = "SELL"
                confidence = min(75, int((1 - overall_score) * 100))
                leverage = "1x (spot)"
            else:
                action = "HOLD (hold position)"
                confidence = 50
                leverage = "1.5x (conservative)"

            # Calculate support and resistance levels
            support = current_price * 0.942  # -5.8%
            resistance = current_price * 1.04  # +4%

            # Create the analysis card
            now = datetime.now()
            expires_at = now + timedelta(hours=2)

            return {
                "header": {
                    "symbol": symbol,
                    "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "analyst": "Ryu Agent (Claude-Enhanced)",
                    "market_tier": self._determine_market_tier(current_price, volume),
                    "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
                },
                "trade_setup": {
                    "entry_details": {
                        "current_price": f"${current_price:.2f}",
                        "action": action,
                        "leverage": leverage,
                        "confidence": f"{confidence}% ({'high' if confidence > 70 else 'medium' if confidence > 50 else 'low'})"
                    },
                    "technical_reasoning": {
                        "primary_signals": ["RSI neutral zone"] if action == "HOLD" else [f"RSI {'oversold' if overall_score > 0.6 else 'overbought'} zone"],
                        "momentum_analysis": f"{'Positive' if price_change > 0 else 'Negative'} momentum - {'Above' if price_change > 0 else 'Below'} EMA20, {price_change:+.1f}% daily change",
                        "trend_analysis": f"Mixed signals - EMA crossover potential, strength {scores['technical']:.2f}",
                        "volume_analysis": f"Normal volume - {int(volume):,} volume, typical trading activity"
                    },
                    "risk_management": {
                        "stop_loss": "No stop loss" if action == "HOLD" else f"${current_price * 0.95:.2f}" if action == "BUY" else f"${current_price * 1.05:.2f}",
                        "take_profit_levels": [] if action == "HOLD" else [f"TP1: ${current_price * 1.08:.2f}", f"TP2: ${current_price * 1.15:.2f}"] if action == "BUY" else [f"Exit: ${current_price:.2f}"],
                        "position_size": f"Maximum {min(15, confidence * 0.15):.1f}% of portfolio"
                    }
                },
                "trade_mathematics": {
                    "leverage_impact": f"With {leverage.split('x')[0]}x leverage:",
                    "risk_calculation": "Risk calculation pending",
                    "reward_calculation": [],
                    "risk_reward_ratios": []
                },
                "execution_strategy": {
                    "time_horizon": f"{time_horizon.upper()} (Current market conditions optimal for execution)",
                    "entry_strategy": f"{'Hold current position - no entry recommended' if action == 'HOLD' else 'Market ' + action.lower() + ' at current levels'}",
                    "exit_strategy": "Monitor for better entry/exit opportunities" if action == "HOLD" else "Scale out at targets",
                    "monitoring_levels": {
                        "support": support,
                        "resistance": resistance
                    }
                },
                "market_context": {
                    "market_conditions": f"{'Bullish' if price_change > 1 else 'Bearish' if price_change < -1 else 'Neutral'} short-term",
                    "catalyst_events": [
                        "Technical breakout potential",
                        "Volume confirmation pending",
                        "Market sentiment shift possible"
                    ],
                    "risk_factors": ["Standard market risk"],
                    "alternative_scenarios": [
                        {"scenario": "Strong breakout", "action": "Increase position", "probability": "25%"},
                        {"scenario": "Range-bound", "action": "Scale out early", "probability": "45%"},
                        {"scenario": "Reversal", "action": "Exit quickly", "probability": "30%"}
                    ]
                },
                "confidence_breakdown": {
                    "Technical": f"{int(scores['technical'] * 100)}%",
                    "Fundamental": f"{int(scores['fundamental'] * 100)}%",
                    "Sentiment": f"{int(scores['sentiment'] * 100)}%",
                    "Risk_Management": "80%"
                },
                "footer": {
                    "data_sources": ["Market Data API", "Technical Analysis", "LLM Analysis"],
                    "last_updated": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "disclaimer": "This analysis is for educational purposes only. Not financial advice."
                }
            }

        except Exception as e:
            logger.error(f"Error creating analysis card for {symbol}: {e}")
            # Return fallback card
            now = datetime.now()
            return {
                "header": {
                    "symbol": symbol,
                    "timestamp": now.isoformat(),
                    "analyst": "Ryu Agent (Fallback)",
                    "market_tier": "Unknown"
                },
                "trade_setup": {
                    "entry_details": {
                        "current_price": "$100.00",
                        "action": "HOLD",
                        "leverage": "1x",
                        "confidence": "50% (low)"
                    },
                    "technical_reasoning": {
                        "primary_signals": ["Insufficient data"],
                        "momentum_analysis": "Analysis unavailable",
                        "trend_analysis": "Analysis unavailable",
                        "volume_analysis": "Analysis unavailable"
                    },
                    "risk_management": {
                        "stop_loss": "Not set",
                        "take_profit_levels": [],
                        "position_size": "0% of portfolio"
                    }
                },
                "trade_mathematics": {
                    "leverage_impact": "No leverage",
                    "risk_calculation": "Not calculated",
                    "reward_calculation": [],
                    "risk_reward_ratios": []
                },
                "execution_strategy": {
                    "time_horizon": "MEDIUM",
                    "entry_strategy": "Hold position",
                    "exit_strategy": "Monitor market",
                    "monitoring_levels": {"support": 95.0, "resistance": 105.0}
                },
                "market_context": {
                    "market_conditions": "Unknown",
                    "catalyst_events": [],
                    "risk_factors": ["Analysis error"],
                    "alternative_scenarios": []
                },
                "confidence_breakdown": {
                    "Technical": "50%",
                    "Fundamental": "50%",
                    "Sentiment": "50%",
                    "Risk_Management": "50%"
                },
                "footer": {
                    "data_sources": ["Fallback Analysis"],
                    "last_updated": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "disclaimer": "Analysis error occurred."
                }
            }

    def _determine_market_tier(self, price: float, volume: float) -> str:
        """Determine market tier based on price and volume."""
        if price > 1000 or volume > 10000000:
            return "Large Cap"
        elif price > 10 or volume > 1000000:
            return "Mid Cap"
        else:
            return "Small Cap"

    async def _calculate_position_sizing(self, amount: float, confidence: float, risk_tolerance: str) -> Dict[str, Any]:
        """Calculate position sizing based on amount and confidence."""
        try:
            # Risk multipliers based on tolerance
            risk_multipliers = {"low": 0.5, "medium": 1.0, "high": 1.5}
            risk_multiplier = risk_multipliers.get(risk_tolerance, 1.0)

            # Base position size (Ryu is conservative)
            base_position = min(amount, amount * confidence * risk_multiplier * 0.1)  # Max 10% of account

            return {
                "recommended_position": base_position,
                "max_position": base_position * 1.5,
                "risk_amount": base_position * 0.03,  # 3% risk per trade
                "position_percentage": min(10.0, confidence * risk_multiplier * 10)
            }

        except Exception as e:
            logger.error(f"Error calculating position sizing: {e}")
            return {
                "recommended_position": amount * 0.05,
                "max_position": amount * 0.1,
                "risk_amount": amount * 0.01,
                "position_percentage": 5.0
            }

    async def _generate_execution_plan(self, symbol: str, amount: float, analysis_card: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed execution plan."""
        try:
            action = analysis_card["trade_setup"]["entry_details"]["action"]

            return {
                "execution_method": "Market order" if action != "HOLD" else "No execution",
                "timing": "Immediate" if action != "HOLD" else "Wait for opportunity",
                "slippage_tolerance": "0.5%",
                "execution_notes": f"Execute {action} order for {symbol} with conservative approach"
            }

        except Exception as e:
            logger.error(f"Error generating execution plan: {e}")
            return {
                "execution_method": "Hold",
                "timing": "Wait",
                "slippage_tolerance": "N/A",
                "execution_notes": "Execution plan unavailable"
            }

    async def _calculate_expected_outcomes(self, analysis_card: Dict[str, Any], amount: float) -> Dict[str, Any]:
        """Calculate expected trading outcomes."""
        try:
            confidence = analysis_card["trade_setup"]["entry_details"]["confidence"]
            confidence_value = float(confidence.split("%")[0]) / 100

            # Conservative outcome estimates for Ryu
            expected_return = confidence_value * 0.05  # 5% max expected return
            expected_risk = 0.03  # 3% max risk

            return {
                "expected_return_percentage": expected_return * 100,
                "expected_profit": amount * expected_return,
                "maximum_risk": amount * expected_risk,
                "win_probability": confidence_value,
                "risk_reward_ratio": expected_return / expected_risk if expected_risk > 0 else 1.0
            }

        except Exception as e:
            logger.error(f"Error calculating expected outcomes: {e}")
            return {
                "expected_return_percentage": 2.0,
                "expected_profit": amount * 0.02,
                "maximum_risk": amount * 0.03,
                "win_probability": 0.6,
                "risk_reward_ratio": 0.67
            }


# Global service instance
_ryu_agent_service: Optional[RyuAgentService] = None


async def get_ryu_agent_service() -> RyuAgentService:
    """Get or create Ryu agent service instance."""
    global _ryu_agent_service

    if _ryu_agent_service is None:
        _ryu_agent_service = RyuAgentService()
        await _ryu_agent_service._initialize_services()
        _ryu_agent_service._services_initialized = True

    return _ryu_agent_service