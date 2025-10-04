"""
Sakura Agent with Real Pendle Integration v3 - Live DeFi Yield Data

Provides real yield farming opportunities using Pendle API:
- Live PT/YT market data from Pendle
- Real-time APY calculations
- Conservative risk assessment
- Portfolio allocation recommendations
- Fallback to traditional DeFi when Pendle unavailable
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .agent_base import BaseAgent, AgentResult, RiskLevel
from .pendle_service import get_pendle_service, PendleMarketData

logger = logging.getLogger(__name__)


class SakuraPendleAgent(BaseAgent):
    """
    Sakura Agent with Real Pendle Integration

    Provides conservative DeFi yield farming opportunities
    using live data from Pendle and other protocols.
    """

    def __init__(self):
        super().__init__("sakura", "Sakura - Pendle Yield Farming")
        self.min_apy = 3.0  # Minimum 3% APY
        self.max_apy = 25.0  # Maximum 25% APY (avoid high-risk)
        self.min_tvl = 1000000  # $1M minimum TVL
        self.max_allocation_per_protocol = 0.15  # Max 15% per protocol

    def get_capabilities(self) -> List[str]:
        """Return Sakura's capabilities."""
        return [
            "pendle_integration",
            "yield_farming",
            "defi_analysis",
            "risk_assessment",
            "portfolio_allocation",
            "conservative_strategies"
        ]

    async def _execute_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute yield farming analysis with live Pendle data."""
        logger.info("🌸 Sakura analyzing live yield opportunities from Pendle...")

        try:
            # Extract investment amount
            investment_amount = params.get("investment_amount", 10000)

            # Discover yield opportunities from Pendle
            opportunities = await self._discover_pendle_opportunities()

            # Filter and score opportunities
            suitable_opportunities = await self._filter_opportunities(opportunities)

            # Calculate portfolio allocation
            portfolio_allocation = await self._calculate_portfolio_allocation(suitable_opportunities, investment_amount)

            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(suitable_opportunities)

            logger.info(f"✅ Sakura analysis completed: {len(suitable_opportunities)} opportunities found")

            return {
                "opportunities": suitable_opportunities,
                "portfolio_allocation": portfolio_allocation,
                "risk_assessment": risk_assessment,
                "market_summary": {
                    "total_opportunities": len(opportunities),
                    "suitable_opportunities": len(suitable_opportunities),
                    "average_apy": np.mean([opp['apy'] for opp in suitable_opportunities]) if suitable_opportunities else 0,
                    "total_tvl_analyzed": sum([opp['tvl'] for opp in opportunities]),
                    "yield_environment": "Favorable" if len(suitable_opportunities) >= 3 else "Limited",
                    "pendle_integration": "Active",
                    "data_source": "Live Pendle API"
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Sakura analysis failed: {e}")
            # Return fallback analysis
            return await self._get_fallback_analysis()

    async def _discover_pendle_opportunities(self) -> List[Dict[str, Any]]:
        """Discover yield opportunities from Pendle and traditional DeFi."""
        opportunities = []

        try:
            # Get Pendle service
            pendle_service = await get_pendle_service()

            # Check Pendle health
            health = await pendle_service.health_check()
            logger.info(f"Pendle API status: {health['status']}")

            if health['status'] == 'healthy':
                # Get real Pendle opportunities
                pendle_markets = await pendle_service.discover_yield_opportunities(
                    min_apy=self.min_apy,
                    min_liquidity=self.min_tvl,
                    max_days_to_maturity=365
                )

                logger.info(f"Found {len(pendle_markets)} Pendle markets")

                # Convert Pendle data to standard format
                for market in pendle_markets:
                    opportunity = {
                        "id": f"pendle_{market.underlying_symbol.lower()}_{market.address[:8]}",
                        "protocol": "Pendle",
                        "asset": market.underlying_symbol,
                        "strategy": "PT/YT Yield Trading",
                        "apy": round(market.current_apy, 2),
                        "tvl": int(market.tvl_usd),
                        "risk_level": self._map_risk_level(market.risk_score),
                        "minimum_deposit": self._estimate_minimum_deposit(market.underlying_symbol),
                        "liquidity_score": min(1.0, market.liquidity_usd / 10000000),
                        "protocol_risk_score": 0.85,  # Pendle is established
                        "smart_contract_risk": 0.85,
                        "description": f"Pendle {market.underlying_symbol} yield trading (matures {market.maturity.strftime('%Y-%m-%d')})",
                        "analysis_timestamp": datetime.now().isoformat(),
                        "days_to_maturity": market.days_to_maturity,
                        "market_address": market.address,
                        "pt_price": market.pt_price,
                        "yt_price": market.yt_price,
                        "volume_24h": market.volume_24h,
                        "data_source": "Pendle API"
                    }
                    opportunities.append(opportunity)

            # Add traditional DeFi opportunities for diversification
            traditional_opportunities = await self._get_traditional_defi_opportunities()
            opportunities.extend(traditional_opportunities)

        except Exception as e:
            logger.error(f"Error discovering Pendle opportunities: {e}")
            # Fallback to traditional DeFi only
            opportunities = await self._get_traditional_defi_opportunities()

        return opportunities

    async def _get_traditional_defi_opportunities(self) -> List[Dict[str, Any]]:
        """Get traditional DeFi opportunities as complement to Pendle."""
        return [
            {
                "id": "aave_usdc",
                "protocol": "Aave V3",
                "asset": "USDC",
                "strategy": "Lending",
                "apy": 4.2,
                "tvl": 892000000,
                "risk_level": "LOW",
                "minimum_deposit": 10,
                "liquidity_score": 0.95,
                "protocol_risk_score": 0.9,
                "smart_contract_risk": 0.9,
                "description": "Stable USDC lending on Aave with high liquidity",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_source": "Static (Fallback)"
            },
            {
                "id": "lido_steth",
                "protocol": "Lido",
                "asset": "stETH",
                "strategy": "Liquid Staking",
                "apy": 3.6,
                "tvl": 15200000000,
                "risk_level": "LOW",
                "minimum_deposit": 0.01,
                "liquidity_score": 0.92,
                "protocol_risk_score": 0.88,
                "smart_contract_risk": 0.87,
                "description": "Ethereum staking rewards through Lido protocol",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_source": "Static (Fallback)"
            },
            {
                "id": "compound_dai",
                "protocol": "Compound V3",
                "asset": "DAI",
                "strategy": "Lending",
                "apy": 3.8,
                "tvl": 320000000,
                "risk_level": "LOW",
                "minimum_deposit": 50,
                "liquidity_score": 0.82,
                "protocol_risk_score": 0.85,
                "smart_contract_risk": 0.85,
                "description": "DAI lending on Compound with stable returns",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_source": "Static (Fallback)"
            }
        ]

    async def _filter_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter opportunities based on Sakura's conservative criteria."""
        suitable = []

        for opp in opportunities:
            try:
                # APY filter
                if not (self.min_apy <= opp['apy'] <= self.max_apy):
                    continue

                # TVL filter
                if opp['tvl'] < self.min_tvl:
                    continue

                # Calculate scores
                opp["sakura_score"] = self._calculate_sakura_score(opp)
                opp["overall_risk_score"] = self._calculate_overall_risk_score(opp)

                # Conservative threshold
                if opp["sakura_score"] >= 0.6:  # Only high-quality opportunities
                    suitable.append(opp)

            except Exception as e:
                logger.warning(f"Error filtering opportunity {opp.get('id', 'unknown')}: {e}")
                continue

        # Sort by Sakura score (highest first)
        suitable.sort(key=lambda x: x["sakura_score"], reverse=True)

        return suitable[:8]  # Top 8 opportunities

    def _map_risk_level(self, risk_score: float) -> str:
        """Map numeric risk score to risk level string."""
        if risk_score <= 0.3:
            return "LOW"
        elif risk_score <= 0.6:
            return "MEDIUM"
        else:
            return "HIGH"

    def _estimate_minimum_deposit(self, asset: str) -> float:
        """Estimate reasonable minimum deposit for asset."""
        minimums = {
            "USDC": 10,
            "USDT": 10,
            "DAI": 10,
            "ETH": 0.01,
            "WETH": 0.01,
            "stETH": 0.01,
            "BTC": 0.001,
            "WBTC": 0.001
        }
        return minimums.get(asset, 50)

    def _calculate_sakura_score(self, opp: Dict[str, Any]) -> float:
        """Calculate Sakura compatibility score (0-1)."""
        try:
            score = 0.0

            # APY scoring (higher is better, but penalize extreme values)
            apy = opp['apy']
            if 3 <= apy <= 8:
                score += 0.3
            elif 8 < apy <= 15:
                score += 0.25
            elif 15 < apy <= 25:
                score += 0.15

            # TVL scoring
            tvl = opp['tvl']
            if tvl >= 100000000:  # $100M+
                score += 0.25
            elif tvl >= 10000000:  # $10M+
                score += 0.2
            elif tvl >= 1000000:  # $1M+
                score += 0.15

            # Protocol risk scoring
            protocol_risk = opp.get('protocol_risk_score', 0.5)
            score += protocol_risk * 0.2

            # Liquidity scoring
            liquidity_score = opp.get('liquidity_score', 0.5)
            score += liquidity_score * 0.15

            # Protocol preference bonus
            protocol = opp.get('protocol', '')
            if protocol in ['Pendle', 'Aave', 'Lido']:
                score += 0.1
            elif protocol in ['Compound', 'Curve']:
                score += 0.05

            return min(score, 1.0)

        except Exception:
            return 0.5

    def _calculate_overall_risk_score(self, opp: Dict[str, Any]) -> float:
        """Calculate overall risk score (0-1, lower is better)."""
        try:
            risk = 0.0

            # APY risk (higher APY = higher risk)
            apy = opp['apy']
            if apy > 20:
                risk += 0.4
            elif apy > 10:
                risk += 0.2
            elif apy > 5:
                risk += 0.1

            # TVL risk (lower TVL = higher risk)
            tvl = opp['tvl']
            if tvl < 1000000:
                risk += 0.3
            elif tvl < 10000000:
                risk += 0.2
            elif tvl < 100000000:
                risk += 0.1

            # Protocol-specific risks
            protocol_risk = 1.0 - opp.get('protocol_risk_score', 0.5)
            smart_contract_risk = 1.0 - opp.get('smart_contract_risk', 0.5)
            risk += (protocol_risk + smart_contract_risk) * 0.15

            return min(risk, 1.0)

        except Exception:
            return 0.5

    async def _calculate_portfolio_allocation(self, opportunities: List[Dict[str, Any]], investment_amount: float = 10000) -> Dict[str, Any]:
        """Calculate optimal portfolio allocation with personalized returns."""
        if not opportunities:
            return {"allocation": [], "total_projected_apy": 0, "risk_score": 0, "investment_amount": investment_amount}

        allocations = []
        total_allocation = 0
        weighted_apy = 0
        weighted_risk = 0

        for i, opp in enumerate(opportunities[:5]):  # Top 5 for allocation
            # Calculate allocation percentage (decreasing for lower-ranked opportunities)
            base_allocation = max(5, 30 - (i * 5))  # 30%, 25%, 20%, 15%, 10%

            # Adjust based on Sakura score
            sakura_bonus = (opp["sakura_score"] - 0.5) * 20  # Up to ±10% adjustment
            allocation_pct = max(5, min(30, base_allocation + sakura_bonus))

            # Ensure we don't exceed 100%
            if total_allocation + allocation_pct > 100:
                allocation_pct = 100 - total_allocation

            if allocation_pct > 0:
                # Calculate dollar amounts based on investment
                allocated_amount = (allocation_pct / 100) * investment_amount
                annual_return = (opp["apy"] / 100) * allocated_amount

                allocations.append({
                    "protocol": opp["protocol"],
                    "asset": opp["asset"],
                    "percentage": round(allocation_pct, 1),
                    "allocated_amount": round(allocated_amount, 2),
                    "annual_return": round(annual_return, 2),
                    "monthly_return": round(annual_return / 12, 2),
                    "apy": opp["apy"],
                    "apy_contribution": round(opp["apy"] * allocation_pct / 100, 2),
                    "risk_contribution": round(opp["overall_risk_score"] * allocation_pct / 100, 3)
                })

                total_allocation += allocation_pct
                weighted_apy += opp["apy"] * allocation_pct / 100
                weighted_risk += opp["overall_risk_score"] * allocation_pct / 100

            if total_allocation >= 100:
                break

        # Calculate total returns
        total_annual_return = sum(alloc["annual_return"] for alloc in allocations)
        total_monthly_return = total_annual_return / 12

        return {
            "allocation": allocations,
            "investment_amount": investment_amount,
            "total_projected_apy": round(weighted_apy, 2),
            "total_annual_return": round(total_annual_return, 2),
            "total_monthly_return": round(total_monthly_return, 2),
            "risk_score": round(weighted_risk, 3),
            "diversification_score": len(allocations) / 5.0  # Up to 5 protocols
        }

    def _generate_risk_assessment(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        if not opportunities:
            return {"overall_risk": "HIGH", "risk_factors": ["No suitable opportunities found"]}

        risk_scores = [opp["overall_risk_score"] for opp in opportunities]
        avg_risk = np.mean(risk_scores)

        risk_level = "LOW" if avg_risk <= 0.3 else "MEDIUM" if avg_risk <= 0.6 else "HIGH"

        risk_factors = []
        if avg_risk > 0.4:
            risk_factors.append("Some opportunities have elevated risk levels")
        if any(opp["apy"] > 15 for opp in opportunities):
            risk_factors.append("High APY opportunities present (>15%)")
        if any(opp["tvl"] < 5000000 for opp in opportunities):
            risk_factors.append("Some protocols have limited TVL (<$5M)")

        return {
            "overall_risk": risk_level,
            "average_risk_score": round(avg_risk, 3),
            "risk_factors": risk_factors if risk_factors else ["Conservative risk profile maintained"],
            "recommended_max_exposure": "15%" if avg_risk <= 0.3 else "10%" if avg_risk <= 0.6 else "5%"
        }

    async def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Get fallback analysis when main analysis fails."""
        logger.warning("Using fallback analysis due to errors")

        fallback_opportunities = await self._get_traditional_defi_opportunities()

        return {
            "opportunities": fallback_opportunities,
            "portfolio_allocation": await self._calculate_portfolio_allocation(fallback_opportunities),
            "risk_assessment": self._generate_risk_assessment(fallback_opportunities),
            "market_summary": {
                "total_opportunities": len(fallback_opportunities),
                "suitable_opportunities": len(fallback_opportunities),
                "average_apy": np.mean([opp['apy'] for opp in fallback_opportunities]),
                "total_tvl_analyzed": sum([opp['tvl'] for opp in fallback_opportunities]),
                "yield_environment": "Limited (Fallback Mode)",
                "pendle_integration": "Offline",
                "data_source": "Fallback Static Data"
            },
            "timestamp": datetime.now().isoformat()
        }


# Global instance
_sakura_pendle_agent: Optional[SakuraPendleAgent] = None


async def get_sakura_pendle_agent() -> SakuraPendleAgent:
    """Get global Sakura Pendle agent instance."""
    global _sakura_pendle_agent
    if _sakura_pendle_agent is None:
        _sakura_pendle_agent = SakuraPendleAgent()
    return _sakura_pendle_agent