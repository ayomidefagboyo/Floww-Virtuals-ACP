"""
Ryu Agent Service - Token Analysis with Flow 3.0 Structure

Based on the comprehensive Flow 3.0 token analysis system, this service provides:
- Complete token analysis with detailed view_insights
- Real Binance market data integration
- Claude AI analysis for detailed reasoning
- Risk factors and comprehensive analysis structure
- Compatible with original Flow 3.0 response format

Ryu is the balanced trading agent focused on moderate risk with thorough analysis.
"""

import asyncio
import logging
import numpy as np
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from decimal import Decimal
from enum import Enum
import uuid

import anthropic
from app.services.binance_service import BinanceService
from app.services.llm_analysis_service import LLMAnalysisService

logger = logging.getLogger(__name__)


@dataclass
class TokenAnalysisResult:
    """Complete token analysis result matching Flow 3.0 structure."""
    id: str
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0-1.0
    current_price: float
    reasoning: str  # Real AI analysis from Claude
    key_factors: List[str]
    time_horizon: str
    risk_level: str  # LOW, MEDIUM, HIGH, EXTREME
    risk_factors: List[str]  # Detailed risk analysis
    view_insights: Dict[str, Any]  # Detailed insights for modal
    expires_at: str
    # Additional Flow 3.0 fields
    entry_strategy: Optional[Dict[str, Any]] = None
    price_targets: Optional[Dict[str, Any]] = None
    risk_management: Optional[Dict[str, Any]] = None
    market_analysis: Optional[Dict[str, Any]] = None


@dataclass
class TechnicalAnalysis:
    """Technical analysis data."""
    rsi_14: float
    macd_line: float
    macd_signal: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_position: float  # 0.0-1.0 position within bands
    volume_sma_20: float
    momentum_score: float
    strength_score: float


@dataclass
class MarketContext:
    """Market context for LLM analysis."""
    timestamp: datetime
    symbol: str
    current_price: float
    price_change_24h: float
    volume_24h: float
    volatility: float
    rsi: float
    macd: float
    bb_position: float  # Position within Bollinger Bands (0-1)
    fear_greed_index: int
    social_sentiment: str
    news_sentiment: str
    funding_rate: float = 0.0001
    market_narrative: str = ""


class RyuAgentService:
    """
    Ryu Agent Service - Token Analysis with Flow 3.0 Structure

    Provides comprehensive token analysis with the same structure as the original
    Flow 3.0 system, including view_insights, risk_factors, and detailed AI analysis.
    """

    def __init__(self):
        self.binance_service = BinanceService()
        self.claude_client = None
        self.api_calls_this_minute = []
        self.max_calls_per_minute = 60

    async def _initialize_services(self):
        """Initialize AI services."""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info("🎯 Ryu agent initialized with Claude AI analysis")
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

    async def analyze_token(
        self,
        symbol: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze token with comprehensive Flow 3.0 structure.
        Main entry point for token analysis.
        """
        try:
            logger.info(f"📊 Ryu token analysis requested for: {symbol}")

            if not hasattr(self, '_services_initialized') or not self._services_initialized:
                await self._initialize_services()
                self._services_initialized = True

            # Validate symbol first
            if not await self._validate_symbol(symbol):
                return {
                    "success": False,
                    "error": f"Symbol {symbol} not found or not supported on Binance",
                    "analysis": None
                }

            # Get comprehensive market data
            market_data = await self._get_comprehensive_market_data(symbol)
            if not market_data:
                return {
                    "success": False,
                    "error": f"Unable to fetch market data for {symbol}",
                    "analysis": None
                }

            # Calculate technical indicators
            technical_data = await self._calculate_technical_indicators(symbol, market_data)

            # Create market context for AI analysis
            market_context = await self._create_market_context(symbol, market_data, technical_data)

            # Get Claude AI analysis
            ai_analysis = await self._get_ai_analysis(market_context)

            # Create comprehensive token analysis result
            analysis_result = await self._create_comprehensive_analysis(
                symbol, market_data, technical_data, ai_analysis
            )

            logger.info(f"✅ Ryu analysis completed for {symbol}: {analysis_result.action} (confidence: {analysis_result.confidence:.1%})")

            return {
                "success": True,
                "analysis": analysis_result
            }

        except Exception as e:
            logger.error(f"❌ Error in Ryu token analysis for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }

    async def _validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol exists on Binance."""
        try:
            # For token analysis, if user provides just 'BTC', convert to 'BTCUSDT'
            if len(symbol) <= 5 and not symbol.endswith('USDT'):
                test_symbol = f"{symbol}USDT"
            else:
                test_symbol = symbol

            # Check if symbol exists in Binance markets using get_symbol_info
            symbol_info = await self.binance_service.get_symbol_info(test_symbol)
            return symbol_info is not None and symbol_info.get('current_price', 0) > 0
        except Exception as e:
            logger.warning(f"Symbol validation failed for {symbol}: {e}")
            return False

    async def _get_comprehensive_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive market data from Binance."""
        try:
            # For token analysis, if user provides just 'BTC', convert to 'BTCUSDT'
            if len(symbol) <= 5 and not symbol.endswith('USDT'):
                pair = f"{symbol}USDT"
            else:
                pair = symbol

            # Use get_symbol_info instead of get_24hr_ticker
            symbol_info = await self.binance_service.get_symbol_info(pair)

            if not symbol_info:
                logger.error(f"No symbol info found for {pair}")
                return None

            # Get kline data for technical analysis
            klines_df = await self.binance_service.get_kline_data(pair, "1h", limit=100)

            current_price = symbol_info.get('current_price', 0)
            price_change_24h = symbol_info.get('price_change_24h', 0)
            volume_24h = symbol_info.get('volume_24h', 0)
            high_24h = symbol_info.get('high_24h', current_price)
            low_24h = symbol_info.get('low_24h', current_price)

            # Convert DataFrame to list for consistency
            klines = klines_df.to_dict('records') if klines_df is not None else []

            return {
                "symbol": symbol,
                "pair": pair,
                "current_price": current_price,
                "price_change_24h": price_change_24h,
                "volume_24h": volume_24h,
                "high_24h": high_24h,
                "low_24h": low_24h,
                "symbol_info": symbol_info,
                "klines_df": klines_df,
                "klines": klines
            }

        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None

    async def _calculate_technical_indicators(self, symbol: str, market_data: Dict[str, Any]) -> TechnicalAnalysis:
        """Calculate comprehensive technical indicators."""
        try:
            klines_df = market_data.get('klines_df')
            current_price = market_data['current_price']
            price_change_24h = market_data['price_change_24h']
            volume_24h = market_data['volume_24h']

            # If we have DataFrame data from BinanceService, use the built-in indicators
            if klines_df is not None and not klines_df.empty and len(klines_df) >= 20:
                # Use BinanceService's technical indicators calculation
                indicators = await self.binance_service.calculate_technical_indicators(market_data['pair'])

                return TechnicalAnalysis(
                    rsi_14=indicators.rsi_14,
                    macd_line=indicators.macd_line,
                    macd_signal=indicators.macd_signal,
                    bb_upper=indicators.bb_upper,
                    bb_middle=indicators.bb_middle,
                    bb_lower=indicators.bb_lower,
                    bb_position=(current_price - indicators.bb_lower) / (indicators.bb_upper - indicators.bb_lower) if indicators.bb_upper > indicators.bb_lower else 0.5,
                    volume_sma_20=volume_24h,  # Use current volume as proxy
                    momentum_score=min(1.0, abs(price_change_24h) / 10),
                    strength_score=max(0, min(1, 0.5 + (price_change_24h / 20)))
                )

            else:
                # Use simplified calculations if not enough data
                rsi = 50 + (price_change_24h * 1.5)
                rsi = max(20, min(80, rsi))

                return TechnicalAnalysis(
                    rsi_14=rsi,
                    macd_line=price_change_24h * 0.1,
                    macd_signal=price_change_24h * 0.08,
                    bb_upper=current_price * 1.02,
                    bb_middle=current_price,
                    bb_lower=current_price * 0.98,
                    bb_position=0.5 + (price_change_24h / 100),
                    volume_sma_20=volume_24h,
                    momentum_score=min(1.0, abs(price_change_24h) / 10),
                    strength_score=max(0, min(1, 0.5 + (price_change_24h / 20)))
                )

        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            # Return fallback values
            current_price = market_data.get('current_price', 100)
            price_change_24h = market_data.get('price_change_24h', 0)

            return TechnicalAnalysis(
                rsi_14=50.0,
                macd_line=0.0,
                macd_signal=0.0,
                bb_upper=current_price * 1.02,
                bb_middle=current_price,
                bb_lower=current_price * 0.98,
                bb_position=0.5,
                volume_sma_20=1000000,
                momentum_score=0.5,
                strength_score=0.5
            )

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator."""
        if len(prices) < period + 1:
            return 50.0

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float]:
        """Calculate MACD line and signal."""
        if len(prices) < 26:
            return 0.0, 0.0

        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26

        # Simplified signal line (would need more sophisticated calculation for real trading)
        macd_signal = macd_line * 0.9

        return macd_line, macd_signal

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return np.mean(prices)

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            mean_price = np.mean(prices)
            std_price = np.std(prices) if len(prices) > 1 else mean_price * 0.02
            return mean_price + (std_dev * std_price), mean_price, mean_price - (std_dev * std_price)

        recent_prices = prices[-period:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)

        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)

        return upper, middle, lower

    async def _create_market_context(self, symbol: str, market_data: Dict[str, Any], technical_data: TechnicalAnalysis) -> MarketContext:
        """Create market context for AI analysis."""
        try:
            current_price = market_data['current_price']
            price_change_24h = market_data['price_change_24h']
            volume_24h = market_data['volume_24h']

            # Create market narrative
            volume_description = "high" if volume_24h > 1000000 else "moderate" if volume_24h > 100000 else "low"
            price_trend = "bullish" if price_change_24h > 2 else "bearish" if price_change_24h < -2 else "neutral"

            market_narrative = f"{symbol} showing {price_change_24h:+.1f}% movement with {volume_description} volume. Technical setup appears {price_trend}."

            # Simple Fear & Greed approximation
            fear_greed = max(10, min(90, 50 + int(price_change_24h * 3)))

            # Social sentiment based on price action and technical indicators
            if price_change_24h > 3 and technical_data.rsi_14 < 70:
                social_sentiment = "positive"
            elif price_change_24h < -3 and technical_data.rsi_14 > 30:
                social_sentiment = "negative"
            else:
                social_sentiment = "neutral"

            return MarketContext(
                timestamp=datetime.now(),
                symbol=symbol,
                current_price=current_price,
                price_change_24h=price_change_24h,
                volume_24h=volume_24h,
                volatility=abs(price_change_24h) / 100,
                rsi=technical_data.rsi_14,
                macd=technical_data.macd_line,
                bb_position=technical_data.bb_position,
                fear_greed_index=fear_greed,
                social_sentiment=social_sentiment,
                news_sentiment="neutral",
                market_narrative=market_narrative
            )

        except Exception as e:
            logger.error(f"Error creating market context for {symbol}: {e}")
            return MarketContext(
                timestamp=datetime.now(),
                symbol=symbol,
                current_price=market_data.get('current_price', 0),
                price_change_24h=market_data.get('price_change_24h', 0),
                volume_24h=market_data.get('volume_24h', 0),
                volatility=0.02,
                rsi=50,
                macd=0,
                bb_position=0.5,
                fear_greed_index=50,
                social_sentiment="neutral",
                news_sentiment="neutral",
                market_narrative=f"{symbol} analysis"
            )

    async def _get_ai_analysis(self, market_context: MarketContext) -> Dict[str, Any]:
        """Get comprehensive AI analysis from Claude."""
        try:
            if not self.claude_client:
                return self._create_fallback_ai_analysis(market_context)

            if not self._can_make_api_call():
                logger.warning("Rate limit reached for Claude API")
                return self._create_fallback_ai_analysis(market_context)

            prompt = f"""
            As Ryu, the balanced crypto trading agent, analyze {market_context.symbol} for token analysis.

            CURRENT MARKET DATA:
            - Symbol: {market_context.symbol}
            - Price: ${market_context.current_price:.6f}
            - 24h Change: {market_context.price_change_24h:+.2f}%
            - 24h Volume: ${market_context.volume_24h:,.2f}
            - Volatility: {market_context.volatility:.1%}

            TECHNICAL INDICATORS:
            - RSI (14): {market_context.rsi:.1f}
            - MACD: {market_context.macd:.6f}
            - Bollinger Band Position: {market_context.bb_position:.2f} (0=bottom, 1=top)
            - Fear & Greed Index: {market_context.fear_greed_index}/100

            MARKET CONTEXT:
            - Social Sentiment: {market_context.social_sentiment}
            - Market Narrative: {market_context.market_narrative}

            Provide a comprehensive token analysis including:

            1. **Action Decision**: BUY, SELL, or HOLD with clear reasoning
            2. **Confidence Level**: 0.0-1.0 based on signal strength and conviction
            3. **Detailed Analysis**: Explain the technical setup, market conditions, and key factors
            4. **Risk Assessment**: Identify specific risks and overall risk level
            5. **Key Factors**: List 4-6 most important factors influencing the decision
            6. **Time Horizon**: Recommended holding period (short/medium/long-term)

            Format your response as detailed analysis with specific price levels, risk factors, and actionable insights.
            Be specific about entry/exit strategies and risk management approaches.
            """

            self._record_api_call()

            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text

            # Parse the analysis into structured format
            return self._parse_ai_analysis(analysis_text, market_context)

        except Exception as e:
            logger.error(f"Error getting AI analysis: {e}")
            return self._create_fallback_ai_analysis(market_context)

    def _parse_ai_analysis(self, analysis_text: str, market_context: MarketContext) -> Dict[str, Any]:
        """Parse AI analysis text into structured format."""
        try:
            # Extract action (BUY/SELL/HOLD)
            action = "HOLD"
            if "BUY" in analysis_text.upper() and analysis_text.upper().count("BUY") > analysis_text.upper().count("SELL"):
                action = "BUY"
            elif "SELL" in analysis_text.upper():
                action = "SELL"

            # Extract confidence (look for percentages or confidence indicators)
            confidence = 0.6  # Default
            confidence_keywords = {
                "high confidence": 0.8,
                "strong conviction": 0.85,
                "moderate confidence": 0.6,
                "low confidence": 0.4,
                "uncertain": 0.3
            }

            for keyword, conf_level in confidence_keywords.items():
                if keyword in analysis_text.lower():
                    confidence = conf_level
                    break

            # Extract key factors
            key_factors = []
            if "rsi" in analysis_text.lower():
                key_factors.append(f"RSI at {market_context.rsi:.0f}")
            if "volume" in analysis_text.lower():
                key_factors.append("Volume analysis")
            if "bollinger" in analysis_text.lower():
                key_factors.append("Bollinger Band position")
            if "trend" in analysis_text.lower():
                key_factors.append("Trend analysis")
            if "momentum" in analysis_text.lower():
                key_factors.append("Price momentum")
            if "support" in analysis_text.lower() or "resistance" in analysis_text.lower():
                key_factors.append("Support/Resistance levels")

            # Default factors if none found
            if not key_factors:
                key_factors = ["Technical analysis", "Market momentum", "Volume patterns", "Price action"]

            # Determine risk level
            risk_level = "MEDIUM"
            if market_context.volatility > 0.05:
                risk_level = "HIGH"
            elif market_context.volatility < 0.02:
                risk_level = "LOW"

            # Extract time horizon
            time_horizon = "MEDIUM"
            if "short" in analysis_text.lower():
                time_horizon = "SHORT"
            elif "long" in analysis_text.lower():
                time_horizon = "LONG"

            return {
                "action": action,
                "confidence": confidence,
                "reasoning": analysis_text,
                "key_factors": key_factors,
                "risk_level": risk_level,
                "time_horizon": time_horizon
            }

        except Exception as e:
            logger.error(f"Error parsing AI analysis: {e}")
            return self._create_fallback_ai_analysis(market_context)

    def _create_fallback_ai_analysis(self, market_context: MarketContext) -> Dict[str, Any]:
        """Create fallback analysis when AI is unavailable."""
        price_change = market_context.price_change_24h
        rsi = market_context.rsi
        volume = market_context.volume_24h

        # Simple rule-based analysis
        if price_change > 3 and rsi < 70 and volume > 500000:
            action = "BUY"
            confidence = 0.65
            reasoning = f"Technical momentum positive with {price_change:+.1f}% gain, RSI at {rsi:.0f} (not overbought), and strong volume support ({volume:,.0f})."
        elif price_change < -3 and rsi > 30 and volume > 500000:
            action = "SELL"
            confidence = 0.6
            reasoning = f"Technical momentum negative with {price_change:+.1f}% decline, RSI at {rsi:.0f} (not oversold yet), and high volume confirming selling pressure."
        else:
            action = "HOLD"
            confidence = 0.5
            reasoning = f"Mixed technical signals with {price_change:+.1f}% change, RSI at {rsi:.0f}. Market conditions suggest waiting for clearer directional bias."

        key_factors = [
            f"RSI {rsi:.0f}",
            "Price momentum",
            "Volume analysis",
            "Technical confluence"
        ]

        risk_level = "HIGH" if market_context.volatility > 0.05 else "LOW" if market_context.volatility < 0.02 else "MEDIUM"

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "risk_level": risk_level,
            "time_horizon": "MEDIUM"
        }

    async def _create_comprehensive_analysis(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_data: TechnicalAnalysis,
        ai_analysis: Dict[str, Any]
    ) -> TokenAnalysisResult:
        """Create comprehensive token analysis result with Flow 3.0 structure."""
        try:
            current_price = market_data['current_price']
            price_change_24h = market_data['price_change_24h']
            volume_24h = market_data['volume_24h']
            high_24h = market_data['high_24h']
            low_24h = market_data['low_24h']

            # Create detailed risk factors
            risk_factors = []

            # Volatility-based risks
            volatility = abs(price_change_24h) / 100
            if volatility > 0.05:
                risk_factors.append("High volatility creates significant price swing risk")

            # Liquidity risks
            if volume_24h < 100000:
                risk_factors.append("Low trading volume may impact liquidity and execution")

            # Technical risks
            if technical_data.rsi_14 > 70:
                risk_factors.append("Overbought RSI signals potential price correction")
            elif technical_data.rsi_14 < 30:
                risk_factors.append("Oversold RSI indicates continued selling pressure risk")

            # Market risks
            risk_factors.extend([
                "General cryptocurrency market volatility",
                "Regulatory changes affecting crypto markets",
                "Correlation with Bitcoin and major crypto movements"
            ])

            # Create view_insights (detailed insights for modal display) with null-safe formatting
            view_insights = {
                "market_analysis": {
                    "price_action": f"Current price ${current_price or 0:.6f} with {price_change_24h or 0:+.2f}% 24h change",
                    "volume_analysis": f"24h volume: ${volume_24h or 0:,.2f} - {'Strong' if (volume_24h or 0) > 1000000 else 'Moderate' if (volume_24h or 0) > 100000 else 'Weak'} trading activity",
                    "range_analysis": f"Trading range: ${low_24h or current_price:.6f} - ${high_24h or current_price:.6f}",
                    "volatility_assessment": f"Current volatility: {volatility:.1%} ({'High' if volatility > 0.05 else 'Normal' if volatility > 0.02 else 'Low'} risk)"
                },
                "technical_indicators": {
                    "rsi_analysis": f"RSI(14): {technical_data.rsi_14 or 50:.1f} - {self._interpret_rsi(technical_data.rsi_14 or 50)}",
                    "macd_analysis": f"MACD: {technical_data.macd_line or 0:.6f} - {'Bullish' if (technical_data.macd_line or 0) > (technical_data.macd_signal or 0) else 'Bearish'} momentum",
                    "bollinger_analysis": f"BB Position: {technical_data.bb_position or 0.5:.2f} - Trading {'near upper band' if (technical_data.bb_position or 0.5) > 0.8 else 'near lower band' if (technical_data.bb_position or 0.5) < 0.2 else 'in middle range'}",
                    "momentum_score": f"Momentum: {technical_data.momentum_score or 0.5:.1%}",
                    "strength_score": f"Technical strength: {technical_data.strength_score or 0.5:.1%}"
                },
                "ai_insights": {
                    "recommendation": ai_analysis.get('action', 'HOLD'),
                    "confidence_level": f"{ai_analysis.get('confidence', 0.5):.1%}",
                    "reasoning_summary": (ai_analysis.get('reasoning', 'Analysis incomplete')[:200] + "..."
                                        if ai_analysis.get('reasoning') and len(ai_analysis['reasoning']) > 200
                                        else ai_analysis.get('reasoning', 'Analysis incomplete')),
                    "key_factors": ai_analysis.get('key_factors', ['Technical analysis pending'])
                },
                "risk_assessment": {
                    "overall_risk": ai_analysis.get('risk_level', 'MEDIUM'),
                    "primary_risks": risk_factors[:3],  # Top 3 risks
                    "risk_mitigation": self._get_risk_mitigation_advice(ai_analysis.get('action', 'HOLD'), ai_analysis.get('risk_level', 'MEDIUM'))
                }
            }

            # Create entry strategy based on action
            entry_strategy = None
            action = ai_analysis.get('action', 'HOLD')
            confidence = ai_analysis.get('confidence', 0.5)
            if action in ['BUY', 'SELL']:
                entry_strategy = {
                    "optimal_entry": current_price,
                    "entry_range_low": current_price * (0.995 if action == 'BUY' else 1.005),
                    "entry_range_high": current_price * (1.005 if action == 'BUY' else 0.995),
                    "market_order_ok": confidence > 0.7
                }

            # Create price targets
            price_targets = None
            if action == 'BUY':
                price_targets = {
                    "target_1": current_price * 1.05,  # 5% target
                    "target_2": current_price * 1.12,  # 12% target
                    "target_3": current_price * 1.20   # 20% target
                }
            elif action == 'SELL':
                price_targets = {
                    "target_1": current_price * 0.95,  # 5% target
                    "target_2": current_price * 0.88,  # 12% target
                    "target_3": current_price * 0.80   # 20% target
                }

            # Create risk management
            risk_management = None
            risk_level = ai_analysis.get('risk_level', 'MEDIUM')
            if action in ['BUY', 'SELL']:
                risk_management = {
                    "stop_loss": current_price * (0.95 if action == 'BUY' else 1.05),
                    "position_size": f"Maximum {self._get_position_size(confidence, risk_level)}% of portfolio",
                    "max_leverage": "3x" if risk_level == 'LOW' else "2x" if risk_level == 'MEDIUM' else "1x"
                }

            # Generate unique analysis ID
            analysis_id = str(uuid.uuid4())[:8]

            return TokenAnalysisResult(
                id=analysis_id,
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                reasoning=ai_analysis.get('reasoning', 'Analysis completed'),
                key_factors=ai_analysis.get('key_factors', []),
                time_horizon=ai_analysis.get('time_horizon', '24h'),
                risk_level=risk_level,
                risk_factors=risk_factors,
                view_insights=view_insights,
                expires_at=(datetime.now() + timedelta(hours=4)).isoformat(),
                entry_strategy=entry_strategy,
                price_targets=price_targets,
                risk_management=risk_management
            )

        except Exception as e:
            import traceback
            logger.error(f"Error creating comprehensive analysis: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return minimal fallback
            return TokenAnalysisResult(
                id="fallback",
                symbol=symbol,
                action="HOLD",
                confidence=0.5,
                current_price=market_data.get('current_price', 0),
                reasoning="Analysis incomplete due to technical error",
                key_factors=["Technical error"],
                time_horizon="MEDIUM",
                risk_level="HIGH",
                risk_factors=["Analysis incomplete"],
                view_insights={"error": "Technical analysis incomplete"},
                expires_at=(datetime.now() + timedelta(hours=1)).isoformat()
            )

    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value."""
        if rsi > 70:
            return "Overbought condition"
        elif rsi < 30:
            return "Oversold condition"
        elif rsi > 60:
            return "Bullish momentum"
        elif rsi < 40:
            return "Bearish momentum"
        else:
            return "Neutral territory"

    def _get_risk_mitigation_advice(self, action: str, risk_level: str) -> List[str]:
        """Get risk mitigation advice based on action and risk level."""
        advice = []

        if action == "BUY":
            advice.extend([
                "Use stop-loss orders to limit downside risk",
                "Consider position sizing based on portfolio risk tolerance"
            ])
            if risk_level == "HIGH":
                advice.append("Consider reducing position size due to high volatility")
        elif action == "SELL":
            advice.extend([
                "Monitor for reversal signals if selling existing position",
                "Consider partial exits to reduce timing risk"
            ])
        else:  # HOLD
            advice.extend([
                "Monitor key technical levels for entry opportunities",
                "Stay updated on fundamental developments"
            ])

        return advice

    def _get_position_size(self, confidence: float, risk_level: str) -> int:
        """Calculate recommended position size percentage."""
        base_size = confidence * 15  # Max 15% for high confidence

        # Adjust for risk level
        if risk_level == "HIGH":
            base_size *= 0.6  # Reduce for high risk
        elif risk_level == "LOW":
            base_size *= 1.2  # Increase for low risk

        return max(2, min(12, int(base_size)))  # Between 2% and 12%


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