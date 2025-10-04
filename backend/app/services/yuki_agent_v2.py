"""
Yuki Agent v2 - Reliable Market Scanner

Provides real-time market scanning with guaranteed results:
- Scans top trading pairs for opportunities
- Technical analysis with confidence scoring
- Reliable fallback mechanisms
- Clear trade recommendations
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .agent_base import BaseAgent, AgentResult, ActionType, RiskLevel, MarketData, TechnicalIndicators
from .llm_analysis_service import create_llm_analysis_service
from .binance_hybrid_service import get_binance_hybrid_service

logger = logging.getLogger(__name__)


class YukiAgent(BaseAgent):
    """
    Yuki Agent - Reliable Market Scanner

    Scans cryptocurrency markets for trading opportunities
    with technical analysis and confidence scoring.
    """

    def __init__(self):
        super().__init__("yuki", "Yuki - Market Scanner")
        self.min_volume = 500000  # $500k minimum volume
        self.min_price_change = 1.0  # 1% minimum movement
        self.max_opportunities = 8  # Maximum opportunities to return
        self.min_confidence = 0.55

    def get_capabilities(self) -> List[str]:
        """Return Yuki's capabilities."""
        return [
            "market_scanning",
            "opportunity_detection",
            "technical_analysis",
            "momentum_trading",
            "volume_analysis"
        ]

    async def _execute_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive market scan."""
        logger.info("🔍 Yuki starting market scan...")

        # Get market data
        market_tickers = await self._get_market_data()
        if not market_tickers:
            raise ValueError("Unable to fetch market data")

        # Filter and score candidates
        candidates = await self._filter_candidates(market_tickers)
        logger.info(f"📊 Found {len(candidates)} potential candidates")

        # Analyze top candidates
        opportunities = await self._analyze_opportunities(candidates)

        # Filter by confidence and limit results
        high_confidence_opportunities = [
            opp for opp in opportunities
            if opp.get('confidence', 0) >= self.min_confidence
        ][:self.max_opportunities]

        logger.info(f"✅ Yuki scan completed: {len(high_confidence_opportunities)} opportunities found")

        return {
            "opportunities": high_confidence_opportunities,
            "total_scanned": len(market_tickers),
            "candidates_analyzed": len(candidates),
            "market_condition": self._assess_market_condition(high_confidence_opportunities),
            "timestamp": datetime.now().isoformat()
        }

    async def _get_market_data(self) -> List[Dict[str, Any]]:
        """Get market data from Binance."""
        try:
            binance_service = await get_binance_hybrid_service()
            tickers = await binance_service.get_24hr_ticker_stats()
            return tickers or []

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

    async def _filter_candidates(self, tickers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tickers for trading candidates."""
        candidates = []

        for ticker in tickers:
            try:
                symbol = ticker.get('symbol', '')
                volume = float(ticker.get('quoteVolume', 0))
                price_change = float(ticker.get('priceChangePercent', 0))
                price = float(ticker.get('price', 0))

                # Filter criteria
                if not symbol.endswith('USDT'):
                    continue

                # Skip stablecoins
                base_symbol = symbol.replace('USDT', '')
                if base_symbol in ['USDC', 'BUSD', 'DAI', 'TUSD', 'FDUSD']:
                    continue

                # Volume filter
                if volume < self.min_volume:
                    continue

                # Price change filter
                if abs(price_change) < self.min_price_change:
                    continue

                # Price filter (avoid very low-priced coins)
                if price < 0.001:
                    continue

                # Skip extreme movements (potential manipulation)
                if abs(price_change) > 50:
                    continue

                candidates.append(ticker)

            except Exception:
                continue

        # Sort by volume (higher volume = more liquid)
        candidates.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
        return candidates[:50]  # Top 50 by volume

    async def _analyze_opportunities(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze candidates for trading opportunities."""
        opportunities = []

        for candidate in candidates[:20]:  # Analyze top 20 candidates
            try:
                opportunity = await self._analyze_single_opportunity(candidate)
                if opportunity:
                    opportunities.append(opportunity)

            except Exception as e:
                logger.warning(f"Failed to analyze {candidate.get('symbol', 'unknown')}: {e}")

        # Sort by confidence
        opportunities.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return opportunities

    async def _analyze_single_opportunity(self, ticker: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single trading opportunity."""
        try:
            symbol = ticker.get('symbol', '')
            base_symbol = symbol.replace('USDT', '')

            # Get technical indicators
            indicators = await self._get_technical_indicators(symbol)
            if not indicators:
                return None

            # Create market data object
            market_data = MarketData(
                symbol=base_symbol,
                current_price=float(ticker.get('price', 0)),
                price_change_24h=float(ticker.get('priceChangePercent', 0)),
                volume_24h=float(ticker.get('volume', 0)),
                high_24h=float(ticker.get('high', 0)),
                low_24h=float(ticker.get('low', 0))
            )

            # Analyze opportunity
            analysis = await self._perform_opportunity_analysis(market_data, indicators, ticker)

            if analysis['confidence'] < self.min_confidence:
                return None

            return analysis

        except Exception as e:
            logger.warning(f"Single opportunity analysis failed for {symbol}: {e}")
            return None

    async def _get_technical_indicators(self, symbol: str) -> Optional[TechnicalIndicators]:
        """Get technical indicators for symbol."""
        try:
            binance_service = await get_binance_hybrid_service()
            indicators = await binance_service.calculate_technical_indicators(symbol)
            return indicators

        except Exception as e:
            logger.warning(f"Technical indicators failed for {symbol}: {e}")
            return None

    async def _perform_opportunity_analysis(self, market_data: MarketData, indicators: TechnicalIndicators, ticker: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive opportunity analysis."""
        try:
            # Determine direction and confidence
            direction, confidence = self._determine_trade_direction(market_data, indicators)

            # Calculate entry and target levels
            levels = self._calculate_trade_levels(market_data, indicators, direction)

            # Optional: Enhance decision with AI (Claude) if available
            try:
                llm_service = create_llm_analysis_service()
                # Build compact context for AI
                ai_context = {
                    "symbol": market_data.symbol,
                    "direction": "LONG" if direction == ActionType.BUY else "SHORT" if direction == ActionType.SELL else "HOLD",
                    "confidence": confidence,
                    "market_context": {
                        "price": market_data.current_price,
                        "price_change_24h": market_data.price_change_24h,
                        "volume_24h": market_data.volume_24h,
                        "high_24h": market_data.high_24h,
                        "low_24h": market_data.low_24h,
                    },
                    "technical_indicators": {
                        "rsi": getattr(indicators, "rsi_14", 50.0),
                        "macd": getattr(indicators, "macd_line", 0.0),
                        "macd_signal": getattr(indicators, "macd_signal", 0.0),
                        "macd_histogram": getattr(indicators, "macd_histogram", 0.0),
                        "bollinger_position": getattr(indicators, "bb_position", 0.5),
                        "bb_upper": getattr(indicators, "bb_upper", 0.0),
                        "bb_middle": getattr(indicators, "bb_middle", 0.0),
                        "bb_lower": getattr(indicators, "bb_lower", 0.0),
                        "ema_20": getattr(indicators, "ema_20", 0.0),
                        "ema_50": getattr(indicators, "ema_50", 0.0),
                        "sma_20": getattr(indicators, "sma_20", 0.0),
                        "atr_14": getattr(indicators, "atr_14", 0.0),
                        "volume_sma_10": getattr(indicators, "volume_sma_10", 0.0),
                        "volume_ratio": getattr(indicators, "volume_ratio", 1.0),
                        "support_level": getattr(indicators, "support_level", 0.0),
                        "resistance_level": getattr(indicators, "resistance_level", 0.0),
                        "trend_direction": getattr(indicators, "trend_direction", "UNKNOWN"),
                        "momentum_score": getattr(indicators, "momentum_score", 0.0),
                        "strength_score": getattr(indicators, "strength_score", 0.0),
                        "volatility_24h": abs(market_data.price_change_24h),
                    },
                    # NOTE: We can pass OHLCV if available in ticker later
                }

                ai_decision = await llm_service.analyze_trading_context(ai_context)
                if ai_decision:
                    # Direction override if AI confident
                    ai_direction = str(ai_decision.get("direction", "")).upper()
                    ai_conf = float(ai_decision.get("confidence", confidence) or confidence)
                    if ai_direction in ("LONG", "SHORT") and ai_conf >= 0.55:
                        direction = ActionType.BUY if ai_direction == "LONG" else ActionType.SELL
                        # Blend confidence
                        confidence = max(confidence, min(0.95, (confidence + ai_conf) / 2))

                    # AI-proposed levels
                    entry_p = ai_decision.get("entry_price")
                    t1 = ai_decision.get("target_1")
                    t2 = ai_decision.get("target_2")
                    sl = ai_decision.get("stop_loss")
                    # Use AI levels when present and sane
                    def _is_sane(x: Any) -> bool:
                        try:
                            v = float(x)
                            return v > 0 and v < market_data.current_price * 1000
                        except Exception:
                            return False

                    levels = {
                        "entry_price": float(entry_p) if _is_sane(entry_p) else levels["entry_price"],
                        "target_1": float(t1) if _is_sane(t1) else levels["target_1"],
                        "target_2": float(t2) if _is_sane(t2) else levels.get("target_2"),
                        "stop_loss": float(sl) if _is_sane(sl) else levels["stop_loss"],
                    }

                    # Optional leverage if provided
                    leverage = ai_decision.get("leverage")
                else:
                    leverage = None
            except Exception:
                # AI optional path should never break core flow
                leverage = None

            # Assess risk
            risk_level = self.determine_risk_level(
                abs(market_data.price_change_24h) / 100,
                market_data.volume_24h
            )

            # Generate reasoning
            reasoning = self._generate_trade_reasoning(market_data, indicators, direction)

            # Key factors
            key_factors = self._identify_trade_factors(market_data, indicators)

            # Calculate risk/reward ratio
            risk_reward = self._calculate_risk_reward(
                levels['entry_price'],
                levels['target_1'],
                levels['stop_loss'],
                direction
            )

            return {
                "id": f"yuki_{market_data.symbol.lower()}_{datetime.now().strftime('%H%M%S')}",
                "symbol": market_data.symbol,
                "direction": "LONG" if direction == ActionType.BUY else "SHORT" if direction == ActionType.SELL else direction.value,
                "confidence": confidence,
                "entry_price": levels['entry_price'],
                "target_1": levels['target_1'],
                "target_2": levels.get('target_2'),
                "stop_loss": levels['stop_loss'],
                "risk_reward_ratio": risk_reward,
                "time_horizon": self._determine_time_horizon(market_data),
                "reasoning": reasoning,
                "key_factors": key_factors,
                "risk_level": risk_level.value,
                # Optional extra metadata when available
                **({"leverage": leverage} if 'leverage' in locals() and leverage is not None else {}),
                "technical_analysis": {
                    "rsi_14": indicators.rsi_14,
                    "macd_line": indicators.macd_line,
                    "bb_position": indicators.bb_position,
                    "momentum_score": self._calculate_momentum_score(market_data, indicators),
                    "strength_score": self._calculate_strength_score(market_data, indicators)
                },
                "expires_at": (datetime.now() + timedelta(hours=6)).isoformat()
            }

        except Exception as e:
            logger.error(f"Opportunity analysis failed for {market_data.symbol}: {e}")
            return self.generate_fallback_response(market_data.symbol)

    def _determine_trade_direction(self, market_data: MarketData, indicators: TechnicalIndicators) -> tuple[ActionType, float]:
        """Determine trade direction and confidence."""
        try:
            signals = []
            confidence_factors = []

            # RSI momentum signals
            if indicators.rsi_14 < 35 and market_data.price_change_24h > -10:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.8)
            elif indicators.rsi_14 > 65 and market_data.price_change_24h > 5:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.7)

            # MACD signals
            if indicators.macd_line > indicators.macd_signal and indicators.macd_line > 0:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.7)
            elif indicators.macd_line < indicators.macd_signal and indicators.macd_line < 0:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.7)

            # Price momentum signals
            if market_data.price_change_24h > 8 and indicators.rsi_14 < 70:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.6)
            elif market_data.price_change_24h < -8 and indicators.rsi_14 > 30:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.6)

            # Bollinger Band signals
            if indicators.bb_position < 0.25:
                signals.append(ActionType.BUY)
                confidence_factors.append(0.6)
            elif indicators.bb_position > 0.75:
                signals.append(ActionType.SELL)
                confidence_factors.append(0.6)

            # Volume confirmation
            if market_data.volume_24h > 2000000:  # High volume
                for i in range(len(confidence_factors)):
                    confidence_factors[i] += 0.1

            # Determine final direction
            if not signals:
                return ActionType.HOLD, 0.5

            buy_count = signals.count(ActionType.BUY)
            sell_count = signals.count(ActionType.SELL)

            if buy_count > sell_count:
                direction = ActionType.BUY
                confidence = np.mean([cf for i, cf in enumerate(confidence_factors) if signals[i] == ActionType.BUY])
            elif sell_count > buy_count:
                direction = ActionType.SELL
                confidence = np.mean([cf for i, cf in enumerate(confidence_factors) if signals[i] == ActionType.SELL])
            else:
                direction = ActionType.HOLD
                confidence = 0.5

            return direction, min(0.95, max(0.4, confidence))

        except Exception:
            return ActionType.HOLD, 0.5

    def _calculate_trade_levels(self, market_data: MarketData, indicators: TechnicalIndicators, direction: ActionType) -> Dict[str, float]:
        """Calculate entry, target, and stop loss levels."""
        try:
            current_price = market_data.current_price
            volatility = max(0.03, abs(market_data.price_change_24h) / 100)  # Min 3% volatility for active trading

            if direction == ActionType.BUY:
                entry_price = current_price * 0.998  # Small discount
                target_1 = current_price * (1 + volatility * 2.5)
                target_2 = current_price * (1 + volatility * 4)
                stop_loss = current_price * (1 - volatility * 1.8)

            elif direction == ActionType.SELL:
                entry_price = current_price * 1.002  # Small premium for short
                target_1 = current_price * (1 - volatility * 2.5)
                target_2 = current_price * (1 - volatility * 4)
                stop_loss = current_price * (1 + volatility * 1.8)

            else:  # HOLD
                entry_price = current_price
                target_1 = current_price * 1.03
                target_2 = current_price * 1.05
                stop_loss = current_price * 0.97

            return {
                "entry_price": entry_price,
                "target_1": target_1,
                "target_2": target_2,
                "stop_loss": stop_loss
            }

        except Exception:
            return {
                "entry_price": market_data.current_price,
                "target_1": market_data.current_price * 1.03,
                "target_2": market_data.current_price * 1.05,
                "stop_loss": market_data.current_price * 0.97
            }

    def _calculate_risk_reward(self, entry: float, target: float, stop: float, direction: ActionType) -> float:
        """Calculate risk/reward ratio."""
        try:
            if direction == ActionType.BUY:
                reward = target - entry
                risk = entry - stop
            elif direction == ActionType.SELL:
                reward = entry - target
                risk = stop - entry
            else:
                return 1.0

            if risk <= 0:
                return 0.0

            return round(reward / risk, 2)

        except Exception:
            return 1.0

    def _generate_trade_reasoning(self, market_data: MarketData, indicators: TechnicalIndicators, direction: ActionType) -> str:
        """Generate reasoning for the trade."""
        try:
            momentum = "bullish" if market_data.price_change_24h > 0 else "bearish"
            rsi_desc = "oversold" if indicators.rsi_14 < 30 else "overbought" if indicators.rsi_14 > 70 else "neutral"
            volume_desc = "high" if market_data.volume_24h > 2000000 else "moderate"

            reasoning = f"Market scan identified {direction.value.lower()} opportunity with {momentum} momentum "
            reasoning += f"({market_data.price_change_24h:+.1f}%). RSI at {indicators.rsi_14:.1f} shows {rsi_desc} conditions. "
            reasoning += f"MACD {'bullish' if indicators.macd_line > indicators.macd_signal else 'bearish'} with {volume_desc} volume support."

            return reasoning

        except Exception:
            return f"{direction.value} opportunity identified through technical analysis"

    def _identify_trade_factors(self, market_data: MarketData, indicators: TechnicalIndicators) -> List[str]:
        """Identify key trading factors."""
        factors = []

        try:
            # Momentum factor
            if abs(market_data.price_change_24h) > 5:
                factors.append(f"Strong momentum ({market_data.price_change_24h:+.1f}%)")

            # RSI factor
            if indicators.rsi_14 < 35:
                factors.append(f"Oversold RSI ({indicators.rsi_14:.1f})")
            elif indicators.rsi_14 > 65:
                factors.append(f"Overbought RSI ({indicators.rsi_14:.1f})")

            # MACD factor
            if abs(indicators.macd_line - indicators.macd_signal) > 0.001:
                direction = "bullish" if indicators.macd_line > indicators.macd_signal else "bearish"
                factors.append(f"MACD {direction} crossover")

            # Volume factor
            if market_data.volume_24h > 5000000:
                factors.append("High volume confirmation")

            # Bollinger Band factor
            if indicators.bb_position < 0.3:
                factors.append("Near support levels")
            elif indicators.bb_position > 0.7:
                factors.append("Near resistance levels")

            return factors[:4] if factors else ["Technical confluence", "Market momentum"]

        except Exception:
            return ["Technical analysis", "Market scanning"]

    def _calculate_momentum_score(self, market_data: MarketData, indicators: TechnicalIndicators) -> float:
        """Calculate momentum score."""
        try:
            score = 0.0

            # Price momentum (40%)
            if abs(market_data.price_change_24h) > 10:
                score += 0.4
            elif abs(market_data.price_change_24h) > 5:
                score += 0.3
            elif abs(market_data.price_change_24h) > 2:
                score += 0.2

            # RSI momentum (30%)
            if 40 <= indicators.rsi_14 <= 60:
                score += 0.3
            elif 30 <= indicators.rsi_14 <= 70:
                score += 0.2
            else:
                score += 0.1

            # MACD momentum (30%)
            if indicators.macd_line > indicators.macd_signal:
                score += 0.3
            else:
                score += 0.1

            return min(1.0, score)

        except Exception:
            return 0.5

    def _calculate_strength_score(self, market_data: MarketData, indicators: TechnicalIndicators) -> float:
        """Calculate strength score."""
        try:
            score = 0.0

            # Volume strength (50%)
            if market_data.volume_24h > 10000000:
                score += 0.5
            elif market_data.volume_24h > 2000000:
                score += 0.4
            elif market_data.volume_24h > 500000:
                score += 0.3
            else:
                score += 0.1

            # Technical strength (50%)
            if indicators.bb_position > 0.8 or indicators.bb_position < 0.2:
                score += 0.2  # Near extremes
            else:
                score += 0.3  # Healthy range

            if abs(indicators.macd_line) > 0.001:
                score += 0.2
            else:
                score += 0.1

            return min(1.0, score)

        except Exception:
            return 0.5

    def _determine_time_horizon(self, market_data: MarketData) -> str:
        """Determine time horizon for the trade."""
        try:
            volatility = abs(market_data.price_change_24h) / 100

            if volatility > 0.15:
                return "1-4 hours"
            elif volatility > 0.08:
                return "4-12 hours"
            else:
                return "12-24 hours"

        except Exception:
            return "4-12 hours"

    def _assess_market_condition(self, opportunities: List[Dict[str, Any]]) -> str:
        """Assess overall market condition based on opportunities."""
        try:
            if not opportunities:
                return "Limited opportunities"

            avg_confidence = np.mean([opp.get('confidence', 0) for opp in opportunities])
            opportunity_count = len(opportunities)

            if avg_confidence > 0.75 and opportunity_count >= 5:
                return "Excellent trading conditions"
            elif avg_confidence > 0.65 and opportunity_count >= 3:
                return "Good trading opportunities"
            elif opportunity_count >= 2:
                return "Moderate opportunities available"
            else:
                return "Limited opportunities"

        except Exception:
            return "Market analysis ongoing"


# Global service instance
_yuki_agent: Optional[YukiAgent] = None


async def get_yuki_agent() -> YukiAgent:
    """Get or create Yuki agent instance."""
    global _yuki_agent
    if _yuki_agent is None:
        _yuki_agent = YukiAgent()
    return _yuki_agent