"""
Pendle API Service - Real-time DeFi Yield Data Integration

Connects to Pendle V2 API to fetch real market data, yield opportunities,
and PT/YT token information for the Sakura agent.

API Documentation: https://api-v2.pendle.finance/core/docs
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class PendleMarketData:
    """Represents Pendle market data from API."""
    address: str
    name: str
    symbol: str
    underlying_symbol: str
    current_apy: float
    implied_apy: float
    liquidity_usd: float
    tvl_usd: float
    pt_price: float
    yt_price: float
    maturity: datetime
    days_to_maturity: int
    risk_score: float
    volume_24h: float


@dataclass
class PendleAsset:
    """Represents Pendle asset information."""
    address: str
    symbol: str
    name: str
    decimals: int
    asset_type: str  # PT, YT, LP, SY
    underlying: str


class PendleAPIService:
    """
    Pendle API client for fetching real-time DeFi yield data.

    Provides access to:
    - Active markets and their APY data
    - PT/YT token information
    - Historical yield data
    - Asset metadata
    """

    def __init__(self):
        self.base_url = "https://api-v2.pendle.finance/core"
        self.session: Optional[aiohttp.ClientSession] = None

        # Supported chains (Ethereum mainnet primary)
        self.supported_chains = {
            "ethereum": 1,
            "arbitrum": 42161,
            "bsc": 56,
            "polygon": 137
        }

        # Default to Ethereum mainnet
        self.default_chain_id = 1

        # Rate limiting tracking
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            import ssl
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "User-Agent": "Floww-Sakura-Agent/1.0",
                    "Accept": "application/json"
                }
            )
        return self.session

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make rate-limited API request to Pendle."""
        try:
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - time_since_last)

            session = await self._get_session()
            url = f"{self.base_url}{endpoint}"

            logger.debug(f"Making Pendle API request: {url}")

            async with session.get(url, params=params) as response:
                self.last_request_time = asyncio.get_event_loop().time()

                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Pendle API response: {response.status}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Pendle API error {response.status}: {error_text}")
                    raise Exception(f"Pendle API error {response.status}: {error_text}")

        except Exception as e:
            logger.error(f"Pendle API request failed: {e}")
            raise

    async def get_active_markets(self, chain_id: int = None) -> List[Dict[str, Any]]:
        """
        Get all active Pendle markets.

        Args:
            chain_id: Blockchain ID (default: Ethereum mainnet)

        Returns:
            List of active market data
        """
        if chain_id is None:
            chain_id = self.default_chain_id

        endpoint = f"/v1/{chain_id}/markets/active"
        response = await self._make_request(endpoint)
        # Extract markets array from response
        return response.get("markets", [])

    async def get_market_data(self, market_address: str, chain_id: int = None) -> Dict[str, Any]:
        """
        Get detailed data for a specific market.

        Args:
            market_address: The market contract address
            chain_id: Blockchain ID (default: Ethereum mainnet)

        Returns:
            Detailed market data including APY, liquidity, etc.
        """
        if chain_id is None:
            chain_id = self.default_chain_id

        endpoint = f"/v2/{chain_id}/markets/{market_address}/data"
        return await self._make_request(endpoint)

    async def get_all_assets(self, chain_id: int = None) -> List[Dict[str, Any]]:
        """
        Get all available PT, YT, LP, SY tokens.

        Args:
            chain_id: Blockchain ID (default: Ethereum mainnet)

        Returns:
            List of all assets with metadata
        """
        if chain_id is None:
            chain_id = self.default_chain_id

        endpoint = f"/v3/{chain_id}/assets/all"
        return await self._make_request(endpoint)

    async def get_market_apy_history(self, market_address: str, chain_id: int = None,
                                   days: int = 7) -> List[Dict[str, Any]]:
        """
        Get historical APY data for a market.

        Args:
            market_address: The market contract address
            chain_id: Blockchain ID (default: Ethereum mainnet)
            days: Number of days of history to fetch

        Returns:
            Historical APY data
        """
        if chain_id is None:
            chain_id = self.default_chain_id

        endpoint = f"/v1/{chain_id}/markets/{market_address}/apy-history"

        # Calculate timestamp for history
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        params = {
            "start": int(start_time.timestamp()),
            "end": int(end_time.timestamp())
        }

        return await self._make_request(endpoint, params)

    async def discover_yield_opportunities(self,
                                         min_apy: float = 3.0,
                                         min_liquidity: float = 1000000,
                                         max_days_to_maturity: int = 365,
                                         chain_id: int = None) -> List[PendleMarketData]:
        """
        Discover available yield opportunities based on criteria.

        Args:
            min_apy: Minimum APY percentage
            min_liquidity: Minimum liquidity in USD
            max_days_to_maturity: Maximum days until maturity
            chain_id: Blockchain ID (default: Ethereum mainnet)

        Returns:
            List of suitable yield opportunities
        """
        try:
            logger.info(f"🔍 Discovering Pendle yield opportunities (min APY: {min_apy}%)")

            # Get all active markets
            markets = await self.get_active_markets(chain_id)

            opportunities = []

            for market in markets:
                try:
                    # Extract market data directly from the response
                    market_address = market.get("address")
                    if not market_address:
                        continue

                    # Get market details from the nested details object
                    details = market.get("details", {})

                    # Extract key data
                    current_apy = details.get("impliedApy", 0) * 100  # Convert to percentage
                    liquidity = details.get("liquidity", 0)  # Already in USD
                    tvl = liquidity  # Use liquidity as TVL for now

                    # Calculate days to maturity
                    expiry_str = market.get("expiry", "")
                    if expiry_str:
                        # Parse ISO date string like "2025-12-25T00:00:00.000Z"
                        from datetime import datetime
                        maturity = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                        days_to_maturity = (maturity - datetime.now().replace(tzinfo=maturity.tzinfo)).days
                    else:
                        days_to_maturity = 0

                    # Apply filters
                    if (current_apy >= min_apy and
                        liquidity >= min_liquidity and
                        days_to_maturity <= max_days_to_maturity and
                        days_to_maturity > 0):

                        # Create market data object
                        market_data = PendleMarketData(
                            address=market_address,
                            name=market.get("name", "Unknown"),
                            symbol=market.get("name", "Unknown"),  # Use name as symbol
                            underlying_symbol=market.get("name", "Unknown"),  # Use name for now
                            current_apy=current_apy,
                            implied_apy=current_apy,
                            liquidity_usd=liquidity,
                            tvl_usd=tvl,
                            pt_price=1.0,  # Default values for now
                            yt_price=1.0,
                            maturity=maturity if expiry_str else datetime.now(),
                            days_to_maturity=days_to_maturity,
                            risk_score=self._calculate_risk_score(current_apy, liquidity, days_to_maturity),
                            volume_24h=0  # Not available in current API response
                        )

                        opportunities.append(market_data)

                except Exception as e:
                    logger.warning(f"Error processing market {market.get('address', 'unknown')}: {e}")
                    continue

            # Sort by APY descending
            opportunities.sort(key=lambda x: x.current_apy, reverse=True)

            logger.info(f"✅ Found {len(opportunities)} suitable Pendle opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error discovering Pendle opportunities: {e}")
            return []

    def _calculate_risk_score(self, apy: float, liquidity: float, days_to_maturity: int) -> float:
        """
        Calculate a risk score based on market characteristics.

        Args:
            apy: Annual percentage yield
            liquidity: Market liquidity in USD
            days_to_maturity: Days until maturity

        Returns:
            Risk score from 0.0 (low risk) to 1.0 (high risk)
        """
        risk_score = 0.0

        # APY risk (higher APY = higher risk)
        if apy > 20:
            risk_score += 0.4
        elif apy > 10:
            risk_score += 0.2
        elif apy > 5:
            risk_score += 0.1

        # Liquidity risk (lower liquidity = higher risk)
        if liquidity < 500000:  # < $500K
            risk_score += 0.3
        elif liquidity < 2000000:  # < $2M
            risk_score += 0.2
        elif liquidity < 5000000:  # < $5M
            risk_score += 0.1

        # Maturity risk (longer maturity = higher risk)
        if days_to_maturity > 300:
            risk_score += 0.3
        elif days_to_maturity > 180:
            risk_score += 0.2
        elif days_to_maturity > 90:
            risk_score += 0.1

        return min(risk_score, 1.0)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Pendle API is accessible.

        Returns:
            Health status information
        """
        try:
            markets = await self.get_active_markets()
            return {
                "status": "healthy",
                "markets_available": len(markets),
                "api_responsive": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "api_responsive": False,
                "timestamp": datetime.now().isoformat()
            }

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global instance
_pendle_service: Optional[PendleAPIService] = None


async def get_pendle_service() -> PendleAPIService:
    """Get global Pendle service instance."""
    global _pendle_service
    if _pendle_service is None:
        _pendle_service = PendleAPIService()
    return _pendle_service


async def close_pendle_service():
    """Close global Pendle service."""
    global _pendle_service
    if _pendle_service:
        await _pendle_service.close()
        _pendle_service = None