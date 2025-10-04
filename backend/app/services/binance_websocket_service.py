"""
Binance WebSocket Service - Real-time Data Streaming

Provides real-time market data via WebSocket to combat API rate limits:
- Live ticker streams for all USDT pairs
- Real-time price updates without rate limits
- Automatic reconnection and error handling
- Memory-efficient data caching
- Fallback to REST API when needed
"""

import asyncio
import json
import logging
import time
import websockets
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class TickerData:
    """Real-time ticker data from WebSocket."""
    symbol: str
    price: float
    price_change: float
    price_change_percent: float
    volume: float
    quote_volume: float
    high: float
    low: float
    open_price: float
    weighted_avg_price: float
    bid_price: float
    ask_price: float
    timestamp: datetime
    count: int = 0  # Number of trades


@dataclass
class MarketSummary:
    """Market summary with statistics."""
    total_pairs: int
    active_pairs: int
    volume_24h_usdt: float
    top_gainers: List[TickerData] = field(default_factory=list)
    top_losers: List[TickerData] = field(default_factory=list)
    high_volume: List[TickerData] = field(default_factory=list)


class BinanceWebSocketService:
    """
    Real-time Binance WebSocket service for efficient market data.

    Maintains live connections to Binance WebSocket streams to avoid
    REST API rate limits while providing real-time market data.
    """

    def __init__(self):
        self.base_ws_url = "wss://stream.binance.com:9443/ws"
        self.ticker_stream_url = "wss://stream.binance.com:9443/ws/!ticker@arr"

        # Data storage
        self.tickers: Dict[str, TickerData] = {}
        self.last_update = datetime.now()
        self.update_callbacks: List[Callable] = []

        # Connection management
        self.ws_connection = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5  # seconds

        # Performance tracking
        self.messages_received = 0
        self.bytes_received = 0
        self.connection_start_time = None

        # Filtering
        self.usdt_pairs_only = True
        self.min_volume_filter = 10000  # Minimum $10k volume

        # Background tasks
        self.ws_task = None
        self.cleanup_task = None
        self.stats_task = None

        logger.info("BinanceWebSocketService initialized")

    async def start(self) -> bool:
        """Start the WebSocket service."""
        try:
            logger.info("🚀 Starting Binance WebSocket service...")

            # Start WebSocket connection
            self.ws_task = asyncio.create_task(self._maintain_connection())

            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_old_data())

            # Start statistics task
            self.stats_task = asyncio.create_task(self._log_statistics())

            # Wait for initial connection
            await self._wait_for_connection(timeout=10)

            logger.info("✅ Binance WebSocket service started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket service: {e}")
            return False

    async def stop(self):
        """Stop the WebSocket service."""
        logger.info("🛑 Stopping Binance WebSocket service...")

        # Cancel background tasks
        for task in [self.ws_task, self.cleanup_task, self.stats_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Close WebSocket connection
        if self.ws_connection:
            await self.ws_connection.close()

        self.is_connected = False
        logger.info("✅ Binance WebSocket service stopped")

    async def _maintain_connection(self):
        """Maintain WebSocket connection with automatic reconnection."""
        while True:
            try:
                logger.info(f"🔌 Connecting to Binance WebSocket: {self.ticker_stream_url}")

                async with websockets.connect(
                    self.ticker_stream_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    self.ws_connection = websocket
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    self.connection_start_time = datetime.now()

                    logger.info("✅ WebSocket connected successfully")

                    # Listen for messages
                    async for message in websocket:
                        await self._handle_message(message)

            except websockets.exceptions.ConnectionClosed:
                logger.warning("🔌 WebSocket connection closed")
                self.is_connected = False

            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                self.is_connected = False

            # Reconnection logic
            if self.reconnect_attempts < self.max_reconnect_attempts:
                self.reconnect_attempts += 1
                wait_time = min(self.reconnect_delay * self.reconnect_attempts, 60)
                logger.info(f"🔄 Reconnecting in {wait_time}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Max reconnection attempts reached")
                break

    async def _handle_message(self, message: str):
        """Handle incoming WebSocket message."""
        try:
            self.messages_received += 1
            self.bytes_received += len(message)

            # Parse JSON message
            data = json.loads(message)

            # Handle ticker array (24hr ticker statistics)
            if isinstance(data, list):
                updated_symbols = []

                for ticker_data in data:
                    symbol = ticker_data.get('s', '')

                    # Filter USDT pairs only
                    if self.usdt_pairs_only and not symbol.endswith('USDT'):
                        continue

                    # Filter low volume pairs
                    quote_volume = float(ticker_data.get('q', 0))
                    if quote_volume < self.min_volume_filter:
                        continue

                    # Create ticker object
                    ticker = TickerData(
                        symbol=symbol,
                        price=float(ticker_data.get('c', 0)),  # Current price
                        price_change=float(ticker_data.get('P', 0)),  # Price change %
                        price_change_percent=float(ticker_data.get('P', 0)),
                        volume=float(ticker_data.get('v', 0)),  # Base volume
                        quote_volume=quote_volume,  # Quote volume
                        high=float(ticker_data.get('h', 0)),  # 24h high
                        low=float(ticker_data.get('l', 0)),   # 24h low
                        open_price=float(ticker_data.get('o', 0)),  # 24h open
                        weighted_avg_price=float(ticker_data.get('w', 0)),  # Weighted avg
                        bid_price=float(ticker_data.get('b', 0)),  # Best bid
                        ask_price=float(ticker_data.get('a', 0)),  # Best ask
                        timestamp=datetime.now(),
                        count=int(ticker_data.get('n', 0))  # Trade count
                    )

                    # Store ticker data
                    self.tickers[symbol] = ticker
                    updated_symbols.append(symbol)

                # Update last update time
                self.last_update = datetime.now()

                # Notify callbacks
                for callback in self.update_callbacks:
                    try:
                        await callback(updated_symbols)
                    except Exception as e:
                        logger.warning(f"Callback error: {e}")

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def _wait_for_connection(self, timeout: int = 10):
        """Wait for WebSocket connection to be established."""
        start_time = time.time()

        while not self.is_connected and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)

        if not self.is_connected:
            raise TimeoutError(f"WebSocket connection not established within {timeout}s")

    async def _cleanup_old_data(self):
        """Clean up old ticker data periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                cutoff_time = datetime.now() - timedelta(minutes=10)
                symbols_to_remove = []

                for symbol, ticker in self.tickers.items():
                    if ticker.timestamp < cutoff_time:
                        symbols_to_remove.append(symbol)

                for symbol in symbols_to_remove:
                    del self.tickers[symbol]

                if symbols_to_remove:
                    logger.info(f"🧹 Cleaned up {len(symbols_to_remove)} old ticker entries")

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def _log_statistics(self):
        """Log performance statistics periodically."""
        while True:
            try:
                await asyncio.sleep(60)  # Log every minute

                if self.connection_start_time:
                    uptime = datetime.now() - self.connection_start_time
                    uptime_seconds = uptime.total_seconds()

                    msg_rate = self.messages_received / max(uptime_seconds, 1)
                    data_rate = self.bytes_received / max(uptime_seconds, 1) / 1024  # KB/s

                    logger.info(
                        f"📊 WebSocket Stats: {len(self.tickers)} pairs, "
                        f"{msg_rate:.1f} msg/s, {data_rate:.1f} KB/s, "
                        f"uptime: {uptime_seconds:.0f}s"
                    )

            except Exception as e:
                logger.error(f"Error in stats task: {e}")

    # Public API Methods

    def add_update_callback(self, callback: Callable):
        """Add callback for ticker updates."""
        self.update_callbacks.append(callback)

    def remove_update_callback(self, callback: Callable):
        """Remove callback for ticker updates."""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    def get_ticker(self, symbol: str) -> Optional[TickerData]:
        """Get current ticker data for a symbol."""
        # Normalize symbol format
        if '/' in symbol:
            symbol = symbol.replace('/', '')
        if not symbol.endswith('USDT'):
            symbol = f"{symbol}USDT"

        return self.tickers.get(symbol)

    def get_all_tickers(self) -> Dict[str, TickerData]:
        """Get all current ticker data."""
        return self.tickers.copy()

    def get_market_summary(self) -> MarketSummary:
        """Get market summary with top movers."""
        if not self.tickers:
            return MarketSummary(0, 0, 0.0)

        # Calculate totals
        total_pairs = len(self.tickers)
        active_pairs = sum(1 for t in self.tickers.values() if t.quote_volume > self.min_volume_filter)
        total_volume = sum(t.quote_volume for t in self.tickers.values())

        # Sort tickers
        tickers_list = list(self.tickers.values())

        # Top gainers (by percentage)
        top_gainers = sorted(
            [t for t in tickers_list if t.price_change_percent > 0],
            key=lambda x: x.price_change_percent,
            reverse=True
        )[:10]

        # Top losers (by percentage)
        top_losers = sorted(
            [t for t in tickers_list if t.price_change_percent < 0],
            key=lambda x: x.price_change_percent
        )[:10]

        # High volume pairs
        high_volume = sorted(
            tickers_list,
            key=lambda x: x.quote_volume,
            reverse=True
        )[:20]

        return MarketSummary(
            total_pairs=total_pairs,
            active_pairs=active_pairs,
            volume_24h_usdt=total_volume,
            top_gainers=top_gainers,
            top_losers=top_losers,
            high_volume=high_volume
        )

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return (
            self.is_connected and
            len(self.tickers) > 100 and  # Should have many pairs
            (datetime.now() - self.last_update).total_seconds() < 30  # Recent updates
        )

    def get_filtered_tickers(
        self,
        min_volume: float = None,
        min_price_change: float = None,
        max_price_change: float = None,
        symbols: List[str] = None
    ) -> List[TickerData]:
        """Get filtered ticker data based on criteria."""
        result = list(self.tickers.values())

        if min_volume is not None:
            result = [t for t in result if t.quote_volume >= min_volume]

        if min_price_change is not None:
            result = [t for t in result if abs(t.price_change_percent) >= min_price_change]

        if max_price_change is not None:
            result = [t for t in result if abs(t.price_change_percent) <= max_price_change]

        if symbols:
            symbol_set = {s.replace('/', '').upper() for s in symbols}
            result = [t for t in result if t.symbol in symbol_set]

        return result

    # Conversion methods for backward compatibility

    def to_rest_format(self, ticker: TickerData) -> Dict[str, Any]:
        """Convert WebSocket ticker to REST API format."""
        return {
            'symbol': ticker.symbol,
            'price': ticker.price,
            'priceChange': ticker.price_change,
            'priceChangePercent': ticker.price_change_percent,
            'volume': ticker.volume,
            'quoteVolume': ticker.quote_volume,
            'high': ticker.high,
            'low': ticker.low,
            'open': ticker.open_price,
            'weightedAvgPrice': ticker.weighted_avg_price,
            'bidPrice': ticker.bid_price,
            'askPrice': ticker.ask_price,
            'count': ticker.count
        }

    async def get_24hr_ticker_stats_ws(self) -> List[Dict[str, Any]]:
        """Get 24hr ticker stats in REST API format from WebSocket data."""
        if not self.is_healthy():
            logger.warning("WebSocket service not healthy, returning empty data")
            return []

        return [
            self.to_rest_format(ticker)
            for ticker in self.tickers.values()
            if ticker.quote_volume >= self.min_volume_filter
        ]


# Global service instance
_ws_service: Optional[BinanceWebSocketService] = None
_ws_service_lock = asyncio.Lock()


async def get_binance_websocket_service() -> BinanceWebSocketService:
    """Get or create WebSocket service instance."""
    global _ws_service

    async with _ws_service_lock:
        if _ws_service is None:
            _ws_service = BinanceWebSocketService()
            # Start service in background
            await _ws_service.start()

        return _ws_service


async def stop_binance_websocket_service():
    """Stop the WebSocket service."""
    global _ws_service

    if _ws_service:
        await _ws_service.stop()
        _ws_service = None