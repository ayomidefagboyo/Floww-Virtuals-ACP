"""
Binance API Service for Real Market Data

Provides real-time market data and technical indicators from Binance API:
- Real-time ticker data and price feeds
- Advanced technical indicators (RSI, MACD, Bollinger Bands)
- Volume analysis and market depth
- 24h statistics and trading pairs
- Rate limiting and error handling
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import ccxt.async_support as ccxt
import pandas as pd
import numpy as np
from collections import deque
import time

logger = logging.getLogger(__name__)


@dataclass
class MarketTicker:
    """Market ticker data structure."""
    symbol: str
    price: float
    price_change_24h: float
    price_change_percent_24h: float
    volume: float
    volume_quote: float
    high_24h: float
    low_24h: float
    open_24h: float
    weighted_avg_price: float
    bid_price: float
    ask_price: float
    timestamp: datetime


@dataclass
class TechnicalIndicators:
    """Technical analysis indicators."""
    rsi_14: float = 50.0
    macd_line: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0
    bb_position: float = 0.5  # 0-1 where price sits in bands
    sma_20: float = 0.0
    ema_20: float = 0.0
    ema_50: float = 0.0
    volume_sma_10: float = 0.0
    atr_14: float = 0.0


class BinanceRateLimiter:
    """Rate limiter to prevent API bans."""

    def __init__(self):
        self.requests_per_minute = 1000
        self.requests_per_second = 16
        self.request_times = deque()
        self.last_request_time = 0
        self.min_request_interval = 1.0 / self.requests_per_second

    async def acquire(self) -> bool:
        """Acquire permission to make a request."""
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        cutoff_time = current_time - 60
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()

        # Check minute-based limit
        if len(self.request_times) >= self.requests_per_minute:
            return False

        # Enforce minimum interval between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
            current_time = time.time()

        # Record this request
        self.request_times.append(current_time)
        self.last_request_time = current_time
        return True


class BinanceService:
    """
    Binance API service for real market data and technical analysis.
    """

    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': '',  # Not needed for public data
            'secret': '',
            'sandbox': False,
            'rateLimit': 50,  # milliseconds between requests
            'enableRateLimit': True,
        })

        self.rate_limiter = BinanceRateLimiter()
        self.price_cache = {}
        self.cache_expiry = 30  # seconds

        logger.info("BinanceService initialized for real market data")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the exchange connection."""
        if self.exchange:
            await self.exchange.close()

    async def get_24hr_ticker_stats(self) -> List[Dict[str, Any]]:
        """
        Get 24hr ticker statistics for all trading pairs.

        Returns real-time market data from Binance.
        """
        try:
            if not await self.rate_limiter.acquire():
                logger.warning("Rate limit exceeded, using cached data")
                return []

            logger.info("Fetching 24hr ticker stats from Binance...")
            tickers = await self.exchange.fetch_tickers()

            result = []
            for symbol, ticker in tickers.items():
                if ticker and 'USDT' in symbol:  # Focus on USDT pairs
                    result.append({
                        'symbol': symbol.replace('/', ''),  # BTCUSDT format
                        'price': float(ticker['last']) if ticker['last'] else 0,
                        'priceChange': float(ticker['change']) if ticker['change'] else 0,
                        'priceChangePercent': float(ticker['percentage']) if ticker['percentage'] else 0,
                        'volume': float(ticker['baseVolume']) if ticker['baseVolume'] else 0,
                        'quoteVolume': float(ticker['quoteVolume']) if ticker['quoteVolume'] else 0,
                        'high': float(ticker['high']) if ticker['high'] else 0,
                        'low': float(ticker['low']) if ticker['low'] else 0,
                        'open': float(ticker['open']) if ticker['open'] else 0,
                        'weightedAvgPrice': float(ticker['vwap']) if ticker['vwap'] else 0,
                        'bidPrice': float(ticker['bid']) if ticker['bid'] else 0,
                        'askPrice': float(ticker['ask']) if ticker['ask'] else 0,
                    })

            logger.info(f"Fetched {len(result)} USDT trading pairs from Binance")
            return result

        except Exception as e:
            logger.error(f"Error fetching ticker stats: {e}")
            return []

    async def get_kline_data(self, symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Get kline/candlestick data for technical analysis.

        Args:
            symbol: Trading pair (e.g. 'BTC/USDT')
            interval: Timeframe ('1m', '5m', '1h', '1d')
            limit: Number of candles to fetch
        """
        try:
            if not await self.rate_limiter.acquire():
                return pd.DataFrame()

            # Normalize symbol format
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    base = symbol[:-4]
                    symbol = f"{base}/USDT"
                else:
                    symbol = f"{symbol}/USDT"

            ohlcv = await self.exchange.fetch_ohlcv(symbol, interval, limit=limit)

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            logger.error(f"Error fetching kline data for {symbol}: {e}")
            return pd.DataFrame()

    async def calculate_technical_indicators(self, symbol: str) -> TechnicalIndicators:
        """
        Calculate technical indicators for a symbol.

        Returns real technical analysis indicators calculated from live data.
        """
        try:
            # Get historical data
            df = await self.get_kline_data(symbol, '1h', 200)

            if df.empty:
                return TechnicalIndicators()

            indicators = TechnicalIndicators()

            # Calculate RSI
            indicators.rsi_14 = self._calculate_rsi(df['close'], 14)

            # Calculate MACD
            macd_line, macd_signal, macd_histogram = self._calculate_macd(df['close'])
            indicators.macd_line = macd_line
            indicators.macd_signal = macd_signal
            indicators.macd_histogram = macd_histogram

            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'], 20, 2)
            indicators.bb_upper = bb_upper
            indicators.bb_middle = bb_middle
            indicators.bb_lower = bb_lower

            # Calculate BB position (where current price sits in the bands)
            current_price = df['close'].iloc[-1]
            if bb_upper > bb_lower:
                indicators.bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            else:
                indicators.bb_position = 0.5

            # Calculate moving averages
            indicators.sma_20 = df['close'].rolling(20).mean().iloc[-1]
            indicators.ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
            indicators.ema_50 = df['close'].ewm(span=50).mean().iloc[-1]

            # Volume indicators
            indicators.volume_sma_10 = df['volume'].rolling(10).mean().iloc[-1]

            # ATR (Average True Range)
            indicators.atr_14 = self._calculate_atr(df, 14)

            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return TechnicalIndicators()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1]) if not rsi.empty else 50.0

        except Exception:
            return 50.0

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Calculate MACD indicator."""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()

            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=signal).mean()
            macd_histogram = macd_line - macd_signal

            return (
                float(macd_line.iloc[-1]) if not macd_line.empty else 0.0,
                float(macd_signal.iloc[-1]) if not macd_signal.empty else 0.0,
                float(macd_histogram.iloc[-1]) if not macd_histogram.empty else 0.0
            )

        except Exception:
            return (0.0, 0.0, 0.0)

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        try:
            sma = prices.rolling(period).mean()
            std = prices.rolling(period).std()

            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)

            return (
                float(upper.iloc[-1]) if not upper.empty else 0.0,
                float(sma.iloc[-1]) if not sma.empty else 0.0,
                float(lower.iloc[-1]) if not lower.empty else 0.0
            )

        except Exception:
            return (0.0, 0.0, 0.0)

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        try:
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()

            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(period).mean()

            return float(atr.iloc[-1]) if not atr.empty else 0.0

        except Exception:
            return 0.0

    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a trading symbol."""
        try:
            if not await self.rate_limiter.acquire():
                return {}

            # Normalize symbol format
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    base = symbol[:-4]
                    symbol = f"{base}/USDT"
                else:
                    symbol = f"{symbol}/USDT"

            # Get ticker info
            ticker = await self.exchange.fetch_ticker(symbol)

            # Get technical indicators
            indicators = await self.calculate_technical_indicators(symbol)

            return {
                'symbol': symbol.replace('/', ''),
                'current_price': ticker['last'],
                'price_change_24h': ticker['percentage'],
                'volume_24h': ticker['baseVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'technical_indicators': {
                    'rsi': indicators.rsi_14,
                    'macd': indicators.macd_line,
                    'bb_position': indicators.bb_position,
                    'sma_20': indicators.sma_20,
                    'ema_20': indicators.ema_20,
                    'ema_50': indicators.ema_50,
                    'atr': indicators.atr_14,
                },
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return {}


# Global service instance
_binance_service = None


async def get_binance_service() -> BinanceService:
    """Get or create Binance service instance."""
    global _binance_service
    if _binance_service is None:
        _binance_service = BinanceService()
    return _binance_service