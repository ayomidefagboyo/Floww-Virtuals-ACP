"""
Binance Hybrid Service - WebSocket + REST API Fallback

Combines WebSocket streaming with REST API fallback to provide:
- Real-time market data via WebSocket (no rate limits)
- Automatic fallback to REST API when WebSocket unavailable
- Technical indicators calculation
- Optimal performance with reliability guarantees
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .binance_websocket_service import get_binance_websocket_service, TickerData
from .binance_service import BinanceService, TechnicalIndicators

logger = logging.getLogger(__name__)


class BinanceHybridService:
    """
    Hybrid Binance service combining WebSocket and REST API.

    Primary: WebSocket for real-time ticker data (no rate limits)
    Fallback: REST API for detailed analysis and when WebSocket unavailable
    """

    def __init__(self):
        self.ws_service = None
        self.rest_service = BinanceService()
        self.use_websocket = True
        self.websocket_healthy = False

        # Performance tracking
        self.websocket_requests = 0
        self.rest_api_requests = 0
        self.cache_hits = 0

        logger.info("BinanceHybridService initialized (WebSocket + REST fallback)")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize the hybrid service."""
        try:
            # Initialize WebSocket service
            self.ws_service = await get_binance_websocket_service()
            self.websocket_healthy = self.ws_service.is_healthy()

            if self.websocket_healthy:
                logger.info("✅ WebSocket service ready - using real-time streams")
            else:
                logger.warning("⚠️ WebSocket service not ready - using REST API fallback")

        except Exception as e:
            logger.error(f"Failed to initialize WebSocket service: {e}")
            self.websocket_healthy = False

    async def close(self):
        """Close the hybrid service."""
        if self.rest_service:
            await self.rest_service.close()

    async def get_24hr_ticker_stats(self) -> List[Dict[str, Any]]:
        """
        Get 24hr ticker statistics with WebSocket priority.

        Uses WebSocket data if available (no rate limits),
        falls back to REST API if needed.
        """
        try:
            # Try WebSocket first
            if self.use_websocket and self.ws_service and self.ws_service.is_healthy():
                logger.debug("📡 Using WebSocket for ticker data")
                self.websocket_requests += 1

                data = await self.ws_service.get_24hr_ticker_stats_ws()
                if data:
                    return data

                logger.warning("WebSocket returned empty data, falling back to REST API")

            # Fallback to REST API
            logger.debug("🌐 Using REST API for ticker data")
            self.rest_api_requests += 1

            return await self.rest_service.get_24hr_ticker_stats()

        except Exception as e:
            logger.error(f"Error getting ticker stats: {e}")
            return []

    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get symbol information with hybrid approach.

        Uses WebSocket for basic price data, REST API for detailed info.
        """
        try:
            result = {}

            # Try to get basic data from WebSocket first
            if self.ws_service and self.ws_service.is_healthy():
                ticker = self.ws_service.get_ticker(symbol)
                if ticker:
                    logger.debug(f"📡 Got {symbol} basic data from WebSocket")
                    self.websocket_requests += 1

                    result = {
                        'symbol': ticker.symbol,
                        'current_price': ticker.price,
                        'price_change_24h': ticker.price_change_percent,
                        'volume_24h': ticker.volume,
                        'high_24h': ticker.high,
                        'low_24h': ticker.low,
                        'quote_volume': ticker.quote_volume,
                        'timestamp': ticker.timestamp.isoformat()
                    }

            # If WebSocket didn't provide data, use REST API
            if not result:
                logger.debug(f"🌐 Getting {symbol} info from REST API")
                self.rest_api_requests += 1
                result = await self.rest_service.get_symbol_info(symbol)

            return result

        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return {}

    async def calculate_technical_indicators(self, symbol: str) -> TechnicalIndicators:
        """
        Calculate technical indicators using REST API.

        Technical indicators require historical data, so we use REST API
        as WebSocket only provides current ticker data.
        """
        try:
            logger.debug(f"📊 Calculating technical indicators for {symbol}")
            self.rest_api_requests += 1

            return await self.rest_service.calculate_technical_indicators(symbol)

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return TechnicalIndicators()

    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive market overview using WebSocket data.

        Provides real-time market statistics without rate limits.
        """
        try:
            if not self.ws_service or not self.ws_service.is_healthy():
                logger.warning("WebSocket not available for market overview")
                return {
                    'total_pairs': 0,
                    'status': 'websocket_unavailable',
                    'timestamp': datetime.now().isoformat()
                }

            logger.debug("📡 Getting market overview from WebSocket")
            self.websocket_requests += 1

            summary = self.ws_service.get_market_summary()

            return {
                'total_pairs': summary.total_pairs,
                'active_pairs': summary.active_pairs,
                'total_volume_24h_usdt': summary.volume_24h_usdt,
                'top_gainers': [
                    {
                        'symbol': t.symbol,
                        'price_change_percent': t.price_change_percent,
                        'volume': t.quote_volume
                    }
                    for t in summary.top_gainers[:5]
                ],
                'top_losers': [
                    {
                        'symbol': t.symbol,
                        'price_change_percent': t.price_change_percent,
                        'volume': t.quote_volume
                    }
                    for t in summary.top_losers[:5]
                ],
                'high_volume': [
                    {
                        'symbol': t.symbol,
                        'volume': t.quote_volume,
                        'price_change_percent': t.price_change_percent
                    }
                    for t in summary.high_volume[:10]
                ],
                'status': 'healthy',
                'data_source': 'websocket',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def scan_for_opportunities(
        self,
        min_volume: float = 500000,
        min_price_change: float = 2.0,
        max_symbols: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scan for trading opportunities using real-time WebSocket data.

        This is extremely efficient as it uses WebSocket data without
        any rate limiting concerns.
        """
        try:
            if not self.ws_service or not self.ws_service.is_healthy():
                logger.warning("WebSocket not available for opportunity scanning")
                return []

            logger.debug(f"🔍 Scanning for opportunities (min_volume: ${min_volume:,.0f})")
            self.websocket_requests += 1

            # Get filtered tickers from WebSocket
            candidates = self.ws_service.get_filtered_tickers(
                min_volume=min_volume,
                min_price_change=min_price_change
            )

            # Sort by combination of volume and price change
            candidates.sort(
                key=lambda t: (abs(t.price_change_percent) * (t.quote_volume / 1000000)),
                reverse=True
            )

            # Take top candidates
            opportunities = []
            for ticker in candidates[:max_symbols]:
                opportunity = {
                    'symbol': ticker.symbol,
                    'current_price': ticker.price,
                    'price_change_24h': ticker.price_change_percent,
                    'volume_24h': ticker.quote_volume,
                    'high_24h': ticker.high,
                    'low_24h': ticker.low,
                    'momentum_score': abs(ticker.price_change_percent) * (ticker.quote_volume / 1000000),
                    'direction': 'BULLISH' if ticker.price_change_percent > 0 else 'BEARISH',
                    'timestamp': ticker.timestamp.isoformat()
                }
                opportunities.append(opportunity)

            logger.info(f"🎯 Found {len(opportunities)} trading opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")
            return []

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics."""
        total_requests = self.websocket_requests + self.rest_api_requests

        return {
            'websocket_requests': self.websocket_requests,
            'rest_api_requests': self.rest_api_requests,
            'cache_hits': self.cache_hits,
            'total_requests': total_requests,
            'websocket_usage_percent': (self.websocket_requests / max(total_requests, 1)) * 100,
            'websocket_healthy': self.websocket_healthy,
            'websocket_connected': self.ws_service.is_connected if self.ws_service else False,
            'active_pairs': len(self.ws_service.tickers) if self.ws_service else 0,
            'last_update': self.ws_service.last_update.isoformat() if self.ws_service else None
        }

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for the hybrid service."""
        try:
            # Check WebSocket health
            ws_healthy = self.ws_service and self.ws_service.is_healthy()

            # Check REST API health (light test)
            rest_healthy = False
            try:
                test_data = await self.rest_service.get_24hr_ticker_stats()
                rest_healthy = len(test_data) > 0
            except Exception:
                rest_healthy = False

            # Overall health
            overall_healthy = ws_healthy or rest_healthy

            return {
                'status': 'healthy' if overall_healthy else 'degraded',
                'websocket': {
                    'healthy': ws_healthy,
                    'connected': self.ws_service.is_connected if self.ws_service else False,
                    'pairs_count': len(self.ws_service.tickers) if self.ws_service else 0
                },
                'rest_api': {
                    'healthy': rest_healthy,
                    'rate_limited': False  # Could add actual rate limit detection
                },
                'performance': self.get_service_stats(),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global service instance
_hybrid_service: Optional[BinanceHybridService] = None


async def get_binance_hybrid_service() -> BinanceHybridService:
    """Get or create hybrid service instance."""
    global _hybrid_service

    if _hybrid_service is None:
        _hybrid_service = BinanceHybridService()
        await _hybrid_service.initialize()

    return _hybrid_service