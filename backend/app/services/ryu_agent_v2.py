"""
Ryu Agent v2 - Reliable Token Analysis

Provides comprehensive token analysis with guaranteed responses:
- Technical analysis with real market data
- AI-enhanced insights when available
- Reliable fallback when AI is unavailable
- Clear risk assessment and recommendations
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .agent_base import BaseAgent, AgentResult, ActionType, RiskLevel, MarketData, TechnicalIndicators
from .binance_hybrid_service import get_binance_hybrid_service

logger = logging.getLogger(__name__)


class RyuAgent(BaseAgent):
    """
    Ryu Agent - Reliable Token Analysis

    Provides comprehensive token analysis with technical indicators,
    risk assessment, and trading recommendations.
    """

    def __init__(self):
        super().__init__("ryu", "Ryu - Token Analysis")
        self.min_confidence = 0.6
        self.analysis_timeout = 25

    def get_capabilities(self) -> List[str]:
        """Return Ryu's capabilities."""
        return [
            "token_analysis",
            "technical_indicators",
            "risk_assessment",
            "entry_exit_levels",
            "confidence_scoring"
        ]

    async def _execute_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive token analysis."""
        symbol = params.get('symbol', '').upper()
        if not symbol:
            raise ValueError("Symbol is required for token analysis")

        logger.info(f"🎯 Ryu analyzing token: {symbol}")

        # Get market data
        market_data = await self._get_market_data(symbol)
        if not market_data:
            raise ValueError(f"Unable to fetch market data for {symbol}")

        # Calculate technical indicators
        technical_indicators = await self._calculate_technical_indicators(symbol)

        # Perform analysis
        analysis = await self._analyze_token(symbol, market_data, technical_indicators)

        logger.info(f"✅ Ryu analysis completed for {symbol}: {analysis['action']} ({analysis['confidence']:.2f})")

        return analysis

    async def _get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data for the symbol."""
        try:
            # Convert symbol to trading pair if needed
            trading_pair = f"{symbol}USDT" if not symbol.endswith('USDT') else symbol

            binance_service = await get_binance_hybrid_service()
            symbol_info = await binance_service.get_symbol_info(trading_pair)

            if not symbol_info:
                return None

            return MarketData(
                symbol=symbol,
                current_price=symbol_info.get('current_price', 0),
                price_change_24h=symbol_info.get('price_change_24h', 0),
                volume_24h=symbol_info.get('volume_24h', 0),
                high_24h=symbol_info.get('high_24h', 0),
                low_24h=symbol_info.get('low_24h', 0),
                market_cap=symbol_info.get('market_cap')
            )

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None

    async def _calculate_technical_indicators(self, symbol: str) -> TechnicalIndicators:
        """Calculate technical indicators for the symbol."""
        try:
            trading_pair = f"{symbol}USDT" if not symbol.endswith('USDT') else symbol

            binance_service = await get_binance_hybrid_service()
            indicators = await binance_service.calculate_technical_indicators(trading_pair)

            return TechnicalIndicators(
                rsi_14=indicators.rsi_14,
                macd_line=indicators.macd_line,
                macd_signal=indicators.macd_signal,
                macd_histogram=indicators.macd_histogram,
                bb_upper=indicators.bb_upper,
                bb_middle=indicators.bb_middle,
                bb_lower=indicators.bb_lower,
                bb_position=indicators.bb_position,
                ema_20=indicators.ema_20,
                ema_50=indicators.ema_50,
                volume_sma_10=indicators.volume_sma_10,
                atr_14=indicators.atr_14
            )

        except Exception as e:
            logger.warning(f"Technical indicators calculation failed for {symbol}: {e}")
            # Return default indicators
            return TechnicalIndicators()

    async def _analyze_token(self, symbol: str, market_data: MarketData, indicators: TechnicalIndicators) -> Dict[str, Any]:
        """Perform comprehensive token analysis."""
        try:
            # Determine trading action based on technical analysis
            action, confidence = self._determine_trading_action(market_data, indicators)

            # Calculate entry and target levels
            entry_levels = self._calculate_entry_levels(market_data, indicators, action)

            # Assess risk
            risk_level = self.determine_risk_level(
                abs(market_data.price_change_24h) / 100,
                market_data.volume_24h
            )

            # Generate reasoning
            reasoning = self._generate_reasoning(market_data, indicators, action, confidence)

            # Key factors
            key_factors = self._identify_key_factors(market_data, indicators)

            # Technical scores
            technical_score = self.calculate_basic_technical_score(indicators)

            return {
                "symbol": symbol,
                "action": action.value,
                "confidence": confidence,
                "current_price": market_data.current_price,
                "reasoning": reasoning,
                "key_factors": key_factors,
                "risk_level": risk_level.value,
                "time_horizon": self._determine_time_horizon(market_data, indicators),
                "entry_strategy": {
                    "optimal_entry": entry_levels["entry"],
                    "entry_range_low": entry_levels["entry_low"],
                    "entry_range_high": entry_levels["entry_high"]
                },
                "price_targets": {
                    "target_1": entry_levels["target_1"],
                    "target_2": entry_levels["target_2"],
                    "stop_loss": entry_levels["stop_loss"]
                },
                "technical_analysis": {
                    "rsi_14": indicators.rsi_14,
                    "macd_line": indicators.macd_line,
                    "bb_position": indicators.bb_position,
                    "technical_score": technical_score
                },
                "market_data": {
                    "price_change_24h": market_data.price_change_24h,
                    "volume_24h": market_data.volume_24h,
                    "volatility": abs(market_data.price_change_24h) / 100
                },
                "expires_at": (datetime.now() + timedelta(hours=4)).isoformat()
            }

        except Exception as e:
            logger.error(f"Token analysis failed for {symbol}: {e}")
            return self.generate_fallback_response(symbol)

    def _determine_trading_action(self, market_data: MarketData, indicators: TechnicalIndicators) -> tuple[ActionType, float]:
        """Determine trading action and confidence based on technical analysis."""
        try:
            signals = []
            confidence_factors = []

            # RSI signals
            if indicators.rsi_14 < 30:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.8)  # Strong oversold signal
            elif indicators.rsi_14 > 70:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.8)  # Strong overbought signal
            elif 40 <= indicators.rsi_14 <= 60:
                signals.append(ActionType.HOLD)
                confidence_factors.append(0.6)  # Neutral zone

            # MACD signals
            if indicators.macd_line > indicators.macd_signal and indicators.macd_line > 0:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.7)
            elif indicators.macd_line < indicators.macd_signal and indicators.macd_line < 0:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.7)

            # Bollinger Band signals
            if indicators.bb_position < 0.2:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.6)
            elif indicators.bb_position > 0.8:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.6)

            # Trend signals
            if indicators.ema_20 > indicators.ema_50:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.5)
            elif indicators.ema_20 < indicators.ema_50:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.5)

            # Volume confirmation
            if market_data.volume_24h > 1000000:  # Good volume
                if len(confidence_factors) > 0:
                    confidence_factors[-1] += 0.1  # Boost latest signal

            # Determine final action
            if not signals:
                return ActionType.HOLD, 0.5

            # Count signals
            buy_count = signals.count(ActionType.BUY)
            sell_count = signals.count(ActionType.SELL)
            hold_count = signals.count(ActionType.HOLD)

            if buy_count > sell_count and buy_count > hold_count:
                action = ActionType.BUY
                confidence = np.mean([cf for i, cf in enumerate(confidence_factors) if signals[i] == ActionType.BUY])
            elif sell_count > buy_count and sell_count > hold_count:
                action = ActionType.SELL
                confidence = np.mean([cf for i, cf in enumerate(confidence_factors) if signals[i] == ActionType.SELL])
            else:
                action = ActionType.HOLD
                confidence = 0.5

            return action, min(0.95, max(0.3, confidence))

        except Exception as e:
            logger.warning(f"Action determination failed: {e}")
            return ActionType.HOLD, 0.5

    def _calculate_entry_levels(self, market_data: MarketData, indicators: TechnicalIndicators, action: ActionType) -> Dict[str, float]:
        """Calculate entry, target, and stop loss levels."""
        try:
            current_price = market_data.current_price
            volatility = max(0.02, abs(market_data.price_change_24h) / 100)  # Min 2% volatility
            atr_estimate = max(indicators.atr_14, current_price * volatility)

            if action == ActionType.BUY:
                entry = current_price * 0.999  # Slight discount
                entry_low = current_price * (1 - volatility * 0.5)
                entry_high = current_price * (1 + volatility * 0.3)
                target_1 = current_price * (1 + volatility * 2)
                target_2 = current_price * (1 + volatility * 3.5)
                stop_loss = current_price * (1 - volatility * 1.5)

            elif action == ActionType.SELL:
                entry = current_price * 1.001  # Slight premium for short
                entry_low = current_price * (1 - volatility * 0.3)
                entry_high = current_price * (1 + volatility * 0.5)
                target_1 = current_price * (1 - volatility * 2)
                target_2 = current_price * (1 - volatility * 3.5)
                stop_loss = current_price * (1 + volatility * 1.5)

            else:  # HOLD
                entry = current_price
                entry_low = current_price * 0.98
                entry_high = current_price * 1.02
                target_1 = current_price * 1.05
                target_2 = current_price * 1.08
                stop_loss = current_price * 0.95

            return {
                "entry": entry,
                "entry_low": entry_low,
                "entry_high": entry_high,
                "target_1": target_1,
                "target_2": target_2,
                "stop_loss": stop_loss
            }

        except Exception as e:
            logger.warning(f"Entry level calculation failed: {e}")
            return {
                "entry": market_data.current_price,
                "entry_low": market_data.current_price * 0.98,
                "entry_high": market_data.current_price * 1.02,
                "target_1": market_data.current_price * 1.05,
                "target_2": market_data.current_price * 1.08,
                "stop_loss": market_data.current_price * 0.95
            }

    def _generate_reasoning(self, market_data: MarketData, indicators: TechnicalIndicators, action: ActionType, confidence: float) -> str:
        """Generate human-readable analysis reasoning."""
        try:
            price_trend = "bullish" if market_data.price_change_24h > 0 else "bearish"
            rsi_condition = "oversold" if indicators.rsi_14 < 30 else "overbought" if indicators.rsi_14 > 70 else "neutral"
            macd_trend = "bullish" if indicators.macd_line > indicators.macd_signal else "bearish"

            reasoning = f"Technical analysis shows {price_trend} momentum with {market_data.price_change_24h:+.1f}% 24h change. "
            reasoning += f"RSI at {indicators.rsi_14:.1f} indicates {rsi_condition} conditions. "
            reasoning += f"MACD shows {macd_trend} divergence. "
            reasoning += f"Confidence: {confidence:.0%} based on indicator confluence."

            return reasoning

        except Exception:
            return f"{action.value} signal based on technical analysis with {confidence:.0%} confidence."

    def _identify_key_factors(self, market_data: MarketData, indicators: TechnicalIndicators) -> List[str]:
        """Identify key factors driving the analysis."""
        factors = []

        try:
            # RSI factor
            if indicators.rsi_14 < 30:
                factors.append(f"Oversold RSI ({indicators.rsi_14:.1f})")
            elif indicators.rsi_14 > 70:
                factors.append(f"Overbought RSI ({indicators.rsi_14:.1f})")

            # MACD factor
            if abs(indicators.macd_line - indicators.macd_signal) > 0.001:
                direction = "bullish" if indicators.macd_line > indicators.macd_signal else "bearish"
                factors.append(f"MACD {direction} crossover")

            # Price momentum
            if abs(market_data.price_change_24h) > 5:
                factors.append(f"Strong momentum ({market_data.price_change_24h:+.1f}%)")

            # Volume factor
            if market_data.volume_24h > 5000000:
                factors.append("High volume confirmation")
            elif market_data.volume_24h < 500000:
                factors.append("Low volume risk")

            # Bollinger band position
            if indicators.bb_position < 0.2:
                factors.append("Near lower Bollinger Band")
            elif indicators.bb_position > 0.8:
                factors.append("Near upper Bollinger Band")

            return factors[:4] if factors else ["Technical analysis", "Market conditions"]

        except Exception:
            return ["Technical analysis", "Market momentum"]

    def _determine_time_horizon(self, market_data: MarketData, indicators: TechnicalIndicators) -> str:
        """Determine appropriate time horizon for the trade."""
        try:
            volatility = abs(market_data.price_change_24h) / 100

            if volatility > 0.15:  # High volatility
                return "1-4 hours"
            elif volatility > 0.08:  # Medium volatility
                return "4-24 hours"
            else:  # Low volatility
                return "1-7 days"

        except Exception:
            return "4-24 hours"


# Global service instance
_ryu_agent: Optional[RyuAgent] = None


async def get_ryu_agent() -> RyuAgent:
    """Get or create Ryu agent instance."""
    global _ryu_agent
    if _ryu_agent is None:
        _ryu_agent = RyuAgent()
    return _ryu_agent