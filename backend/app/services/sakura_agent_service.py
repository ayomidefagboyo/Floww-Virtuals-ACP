"""
Sakura Agent Service - Pendle Yield Farming & Conservative DeFi

Based on the Pendle integration from floww3.0, this service provides:
- Pendle PT/YT market analysis and yield optimization
- Conservative DeFi yield farming strategies
- Multi-layer risk assessment framework
- Portfolio allocation with maximum diversification
- Real-time yield opportunity scanning

Sakura is the conservative agent focused on low-risk, stable yield generation.
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

logger = logging.getLogger(__name__)


@dataclass
class PendleMarket:
    """Represents a Pendle PT/YT market pair."""
    market_address: str
    pt_address: str  # Principal Token
    yt_address: str  # Yield Token
    sy_address: str  # Standardized Yield
    underlying_asset: str
    underlying_symbol: str
    maturity: datetime
    implied_apy: float
    pt_price: float
    yt_price: float
    liquidity_usd: float
    chain_id: int = 8453  # Base mainnet


@dataclass
class PendleYieldOpportunity:
    """Yield opportunity optimized for Sakura's conservative approach."""
    market: PendleMarket
    strategy_type: str  # "fixed_yield", "yield_trading"
    expected_apy: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    time_to_maturity: int  # days
    sakura_score: float  # Compatibility score (0-1)
    current_pt_price: float
    discount_to_maturity: float
    break_even_days: int
    liquidity_score: float
    volatility_score: float
    protocol_risk_score: float


class SakuraAgentService:
    """
    Sakura Agent Service - Conservative Yield Farming

    Provides Pendle yield farming analysis and portfolio optimization
    based on the complete floww3.0 implementation.
    """

    def __init__(self):
        # Conservative risk parameters
        self.max_position_size = 5.0  # 5% max per position
        self.min_yield_apy = 5.0  # Minimum acceptable yield
        self.max_yield_apy = 25.0  # Maximum yield (avoid high-risk)
        self.preferred_timeframe = (90, 365)  # 3-12 months
        self.min_liquidity = 1000000  # $1M minimum liquidity
        self.confidence_threshold = 0.7  # High confidence required

        # Asset preferences (higher score = more preferred)
        self.asset_preferences = {
            "USDC": 1.0,
            "DAI": 1.0,
            "USDT": 0.9,
            "WETH": 0.8,
            "ETH": 0.8,
            "stETH": 0.7
        }

    async def _initialize_services(self):
        """Initialize Pendle and DeFi services."""
        try:
            logger.info("Sakura agent initialized for Pendle yield farming")
        except Exception as e:
            logger.error(f"Error initializing Sakura services: {e}")

    async def analyze_yield_opportunities(self) -> Dict[str, Any]:
        """
        Analyze current yield opportunities in the DeFi market.
        Main entry point for Virtuals ACP integration.
        """
        try:
            logger.info("Analyzing yield opportunities (Sakura agent)")

            if not hasattr(self, '_services_initialized') or not self._services_initialized:
                await self._initialize_services()
                self._services_initialized = True

            # Discover Pendle markets
            markets = await self._discover_pendle_markets()

            # Score opportunities using Sakura's criteria
            opportunities = await self._score_yield_opportunities(markets)

            # Filter to top opportunities
            top_opportunities = [opp for opp in opportunities if opp.sakura_score >= self.confidence_threshold][:5]

            # Calculate portfolio allocation
            portfolio_allocation = await self._calculate_portfolio_allocation(top_opportunities)

            # Generate comprehensive analysis
            analysis = {
                "total_opportunities_found": len(opportunities),
                "suitable_opportunities": len(top_opportunities),
                "top_opportunities": [
                    {
                        "underlying_asset": opp.market.underlying_symbol,
                        "expected_apy": opp.expected_apy,
                        "risk_level": opp.risk_level,
                        "time_to_maturity": opp.time_to_maturity,
                        "sakura_score": opp.sakura_score,
                        "strategy_type": opp.strategy_type,
                        "liquidity_usd": opp.market.liquidity_usd
                    }
                    for opp in top_opportunities
                ],
                "portfolio_allocation": portfolio_allocation,
                "market_summary": {
                    "total_opportunities": len(opportunities),
                    "average_apy": np.mean([opp.expected_apy for opp in opportunities]) if opportunities else 0.0,
                    "max_apy": max([opp.expected_apy for opp in opportunities]) if opportunities else 0.0,
                    "risk_distribution": {
                        "LOW": len([opp for opp in opportunities if opp.risk_level == "LOW"]),
                        "MEDIUM": len([opp for opp in opportunities if opp.risk_level == "MEDIUM"])
                    },
                    "asset_coverage": list(set([opp.market.underlying_symbol for opp in opportunities])),
                    "market_health": self._assess_market_health(opportunities),
                    "yield_environment": "Favorable" if len(top_opportunities) > 0 else "Limited"
                },
                "risk_assessment": await self._generate_risk_assessment(top_opportunities),
                "expected_portfolio_apy": portfolio_allocation.get("expected_apy", 0.0),
                "analysis_timestamp": datetime.now().isoformat()
            }

            logger.info(f"Sakura yield analysis: {len(top_opportunities)} opportunities found, expected portfolio APY: {analysis['expected_portfolio_apy']:.1f}%")

            return {"analysis": analysis}

        except Exception as e:
            logger.error(f"Error analyzing yield opportunities: {e}")
            return {"analysis": None, "error": str(e)}

    async def scan_yield_markets(self, focus_assets: List[str] = None) -> Dict[str, Any]:
        """
        Scan specific yield markets for opportunities.
        """
        try:
            if focus_assets is None:
                focus_assets = ["ETH", "USDC", "stETH"]

            logger.info(f"Scanning yield markets for assets: {focus_assets}")

            # Get market data for focus assets
            markets = await self._discover_pendle_markets()
            filtered_markets = [
                market for market in markets
                if market.underlying_symbol in focus_assets
            ]

            # Score and analyze
            opportunities = await self._score_yield_opportunities(filtered_markets)

            scan_results = []
            for opp in opportunities[:3]:  # Top 3 for each asset
                scan_results.append({
                    "asset": opp.market.underlying_symbol,
                    "strategy": opp.strategy_type,
                    "expected_apy": opp.expected_apy,
                    "risk_level": opp.risk_level,
                    "time_to_maturity": opp.time_to_maturity,
                    "liquidity_usd": opp.market.liquidity_usd,
                    "sakura_score": opp.sakura_score,
                    "recommended_allocation": min(5.0, opp.sakura_score * 5)
                })

            return {
                "scan_results": scan_results,
                "total_markets_scanned": len(filtered_markets),
                "opportunities_found": len(opportunities),
                "focus_assets": focus_assets,
                "scan_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scanning yield markets: {e}")
            return {"scan_results": [], "error": str(e)}

    async def execute_yield_strategy(self, amount: float) -> Dict[str, Any]:
        """
        Execute yield farming strategy with specified amount.
        """
        try:
            logger.info(f"Executing yield strategy with ${amount:.2f}")

            # Get yield analysis first
            analysis_result = await self.analyze_yield_opportunities()
            analysis = analysis_result.get("analysis")

            if not analysis or not analysis.get("top_opportunities"):
                return {"success": False, "error": "No suitable yield opportunities found"}

            top_opportunity = analysis["top_opportunities"][0]

            # Calculate position sizing
            max_allocation = min(amount, amount * 0.05)  # Max 5% allocation
            recommended_amount = max_allocation * (top_opportunity["sakura_score"] * 0.8)

            # Generate execution details
            execution_details = {
                "strategy": "pendle_fixed_yield",
                "underlying_asset": top_opportunity["underlying_asset"],
                "expected_apy": top_opportunity["expected_apy"],
                "investment_amount": recommended_amount,
                "max_allocation": max_allocation,
                "time_horizon_days": top_opportunity["time_to_maturity"],
                "risk_level": top_opportunity["risk_level"],
                "expected_annual_return": recommended_amount * (top_opportunity["expected_apy"] / 100),
                "break_even_days": int(top_opportunity["time_to_maturity"] * 0.1),
                "liquidity_score": 0.8,  # Simplified for demo
                "execution_method": "Pendle PT purchase",
                "slippage_tolerance": "0.5%",
                "execution_timestamp": datetime.now().isoformat()
            }

            return {
                "success": True,
                "yield_strategy": execution_details
            }

        except Exception as e:
            logger.error(f"Error executing yield strategy: {e}")
            return {"success": False, "error": str(e)}

    async def _discover_pendle_markets(self) -> List[PendleMarket]:
        """Discover available Pendle markets."""
        try:
            # Mock Pendle markets - in production this would fetch from Pendle API
            base_timestamp = datetime.now()
            markets = []

            # Generate realistic Pendle PT markets
            market_configs = [
                {
                    "underlying": "USDC",
                    "implied_apy": 12.5,
                    "liquidity": 15000000,  # $15M
                    "pt_price": 0.92,
                    "days_to_maturity": 180
                },
                {
                    "underlying": "ETH",
                    "implied_apy": 8.3,
                    "liquidity": 8000000,  # $8M
                    "pt_price": 0.88,
                    "days_to_maturity": 120
                },
                {
                    "underlying": "stETH",
                    "implied_apy": 15.3,
                    "liquidity": 5000000,  # $5M
                    "pt_price": 0.85,
                    "days_to_maturity": 90
                }
            ]

            for i, config in enumerate(market_configs):
                maturity = base_timestamp + timedelta(days=config["days_to_maturity"])
                market = PendleMarket(
                    market_address=f"0x{''.join(['%02x' % (i*37 + j) for j in range(20)])}",
                    pt_address=f"0x{''.join(['%02x' % (i*41 + j) for j in range(20)])}",
                    yt_address=f"0x{''.join(['%02x' % (i*43 + j) for j in range(20)])}",
                    sy_address=f"0x{''.join(['%02x' % (i*47 + j) for j in range(20)])}",
                    underlying_asset=config["underlying"],
                    underlying_symbol=config["underlying"],
                    maturity=maturity,
                    implied_apy=config["implied_apy"],
                    pt_price=config["pt_price"],
                    yt_price=1.0 - config["pt_price"],
                    liquidity_usd=config["liquidity"]
                )
                markets.append(market)

            logger.info(f"Discovered {len(markets)} Pendle markets")
            return markets

        except Exception as e:
            logger.error(f"Error discovering Pendle markets: {e}")
            return []

    async def _score_yield_opportunities(self, markets: List[PendleMarket]) -> List[PendleYieldOpportunity]:
        """Score yield opportunities using Sakura's criteria."""
        opportunities = []

        for market in markets:
            try:
                # Calculate yield metrics
                days_to_maturity = (market.maturity - datetime.now()).days
                if days_to_maturity <= 0:
                    continue

                # Fixed yield from PT discount
                discount = 1.0 - market.pt_price
                expected_apy = (discount / (days_to_maturity / 365)) * 100

                # Skip if outside acceptable range
                if not (self.min_yield_apy <= expected_apy <= self.max_yield_apy):
                    continue

                # Calculate component scores
                liquidity_score = min(1.0, market.liquidity_usd / 50000000)  # $50M = max score
                maturity_score = self._calculate_maturity_score(days_to_maturity)
                yield_score = self._calculate_yield_score(expected_apy)
                asset_score = self.asset_preferences.get(market.underlying_symbol, 0.5)

                # Overall Sakura compatibility score
                sakura_score = (
                    liquidity_score * 0.30 +
                    maturity_score * 0.25 +
                    yield_score * 0.25 +
                    asset_score * 0.20
                )

                # Determine risk level
                risk_level = self._assess_risk_level(market, expected_apy, liquidity_score)

                # Break-even analysis
                break_even_days = max(30, int(days_to_maturity * 0.1))  # 10% buffer minimum 30 days

                opportunity = PendleYieldOpportunity(
                    market=market,
                    strategy_type="fixed_yield",
                    expected_apy=expected_apy,
                    risk_level=risk_level,
                    time_to_maturity=days_to_maturity,
                    sakura_score=sakura_score,
                    current_pt_price=market.pt_price,
                    discount_to_maturity=discount,
                    break_even_days=break_even_days,
                    liquidity_score=liquidity_score,
                    volatility_score=0.8,  # Simplified
                    protocol_risk_score=0.9  # Pendle is well-established
                )

                opportunities.append(opportunity)

            except Exception as e:
                logger.warning(f"Error scoring opportunity for {market.underlying_symbol}: {e}")
                continue

        # Sort by Sakura score (descending)
        opportunities.sort(key=lambda x: x.sakura_score, reverse=True)
        return opportunities

    def _calculate_maturity_score(self, days_to_maturity: int) -> float:
        """Calculate maturity score based on Sakura's preferences."""
        min_days, max_days = self.preferred_timeframe

        if min_days <= days_to_maturity <= max_days:
            return 1.0
        elif days_to_maturity < min_days:
            return max(0.3, days_to_maturity / min_days)
        else:
            return max(0.3, max_days / days_to_maturity)

    def _calculate_yield_score(self, expected_apy: float) -> float:
        """Calculate yield score based on risk-adjusted expectations."""
        # Optimal range for conservative strategy: 8-15%
        if 8.0 <= expected_apy <= 15.0:
            return 1.0
        elif expected_apy < 8.0:
            return max(0.3, expected_apy / 8.0)
        else:
            # Higher yield = higher risk, penalize slightly
            return max(0.5, 15.0 / expected_apy)

    def _assess_risk_level(self, market: PendleMarket, expected_apy: float, liquidity_score: float) -> str:
        """Assess overall risk level for the opportunity."""
        # Conservative risk assessment
        if (liquidity_score >= 0.8 and
            expected_apy <= 12.0 and
            market.underlying_symbol in ["USDC", "DAI", "USDT"]):
            return "LOW"
        elif liquidity_score >= 0.5 and expected_apy <= 18.0:
            return "MEDIUM"
        else:
            return "HIGH"

    async def _calculate_portfolio_allocation(self, opportunities: List[PendleYieldOpportunity]) -> Dict[str, Any]:
        """Calculate optimal portfolio allocation across opportunities."""
        if not opportunities:
            return {
                "total_allocation": 0,
                "strategies": [],
                "expected_apy": 0.0
            }

        total_score = sum(opp.sakura_score for opp in opportunities)
        allocations = []
        total_allocation = 0
        weighted_apy = 0

        for opp in opportunities:
            # Allocation based on score, capped at 5% per position
            raw_allocation = (opp.sakura_score / total_score) * 25  # Max 25% in yield farming
            capped_allocation = min(5.0, raw_allocation)

            if capped_allocation >= 1.0:  # Minimum 1% to be meaningful
                allocations.append({
                    "asset": opp.market.underlying_symbol,
                    "strategy": opp.strategy_type,
                    "allocation_percent": capped_allocation,
                    "expected_apy": opp.expected_apy,
                    "risk_level": opp.risk_level,
                    "time_horizon_days": opp.time_to_maturity
                })
                total_allocation += capped_allocation
                weighted_apy += opp.expected_apy * (capped_allocation / 25)

        return {
            "total_allocation": total_allocation,
            "strategies": allocations,
            "expected_apy": weighted_apy * (25 / total_allocation) if total_allocation > 0 else 0.0
        }

    async def _generate_risk_assessment(self, opportunities: List[PendleYieldOpportunity]) -> str:
        """Generate comprehensive risk assessment."""
        if not opportunities:
            return "No risk assessment available"

        risk_levels = [opp.risk_level for opp in opportunities]
        low_risk_count = risk_levels.count("LOW")
        medium_risk_count = risk_levels.count("MEDIUM")

        if low_risk_count >= len(opportunities) * 0.8:
            return "LOW - Portfolio dominated by stable yield opportunities with strong liquidity"
        elif medium_risk_count + low_risk_count >= len(opportunities) * 0.9:
            return "MEDIUM - Balanced portfolio with conservative risk profile"
        else:
            return "ELEVATED - Higher risk opportunities present, consider reducing allocation"

    def _assess_market_health(self, opportunities: List[PendleYieldOpportunity]) -> str:
        """Assess overall DeFi yield market health."""
        if not opportunities:
            return "Poor"

        avg_liquidity = np.mean([opp.market.liquidity_usd for opp in opportunities])
        high_score_count = len([opp for opp in opportunities if opp.sakura_score >= 0.8])

        if avg_liquidity > 10000000 and high_score_count >= 3:
            return "Excellent"
        elif avg_liquidity > 5000000 and high_score_count >= 2:
            return "Good"
        elif high_score_count >= 1:
            return "Fair"
        else:
            return "Limited"


# Global service instance
_sakura_agent_service: Optional[SakuraAgentService] = None


async def get_sakura_agent_service() -> SakuraAgentService:
    """Get or create Sakura agent service instance."""
    global _sakura_agent_service

    if _sakura_agent_service is None:
        _sakura_agent_service = SakuraAgentService()
        await _sakura_agent_service._initialize_services()
        _sakura_agent_service._services_initialized = True

    return _sakura_agent_service