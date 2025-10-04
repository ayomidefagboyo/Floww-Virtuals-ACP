"""
Sakura Agent v2 - Reliable Yield Farming Analysis

Provides conservative DeFi yield farming opportunities:
- Real yield opportunity analysis
- Risk-adjusted returns
- Portfolio allocation recommendations
- Conservative approach with safety focus
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .agent_base import BaseAgent, AgentResult, RiskLevel
from .pendle_service import get_pendle_service, PendleMarketData

logger = logging.getLogger(__name__)


class SakuraAgent(BaseAgent):
    """
    Sakura Agent - Reliable Yield Farming Analysis

    Provides conservative DeFi yield farming opportunities
    with focus on risk management and stable returns.
    """

    def __init__(self):
        super().__init__("sakura", "Sakura - Yield Farming")
        self.min_apy = 3.0  # Minimum 3% APY
        self.max_apy = 30.0  # Maximum 30% APY (avoid high-risk)
        self.min_tvl = 1000000  # $1M minimum TVL
        self.max_allocation_per_protocol = 0.15  # Max 15% per protocol

    def get_capabilities(self) -> List[str]:
        """Return Sakura's capabilities."""
        return [
            "yield_farming",
            "defi_analysis",
            "risk_assessment",
            "portfolio_allocation",
            "conservative_strategies"
        ]

    async def _execute_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute yield farming analysis."""
        logger.info("🌸 Sakura analyzing yield opportunities...")

        # Discover yield opportunities
        opportunities = await self._discover_yield_opportunities()

        # Filter and score opportunities
        suitable_opportunities = await self._filter_opportunities(opportunities)

        # Calculate portfolio allocation
        portfolio_allocation = await self._calculate_portfolio_allocation(suitable_opportunities)

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
                "yield_environment": "Favorable" if len(suitable_opportunities) >= 3 else "Limited"
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _discover_yield_opportunities(self) -> List[Dict[str, Any]]:
        """Discover available yield farming opportunities."""
        try:
            # Simulate discovering yield opportunities from various DeFi protocols
            # In a real implementation, this would query actual DeFi APIs
            opportunities = [
                {
                    "id": "aave_usdc",
                    "protocol": "Aave V3",
                    "asset": "USDC",
                    "strategy": "Lending",
                    "apy": 4.8,
                    "tvl": 892000000,  # $892M
                    "risk_level": "LOW",
                    "minimum_deposit": 10,
                    "liquidity_score": 0.95,
                    "protocol_risk_score": 0.9,
                    "smart_contract_risk": 0.9,
                    "description": "Stable lending on Aave with high liquidity"
                },
                {
                    "id": "compound_eth",
                    "protocol": "Compound V3",
                    "asset": "ETH",
                    "strategy": "Collateral Earning",
                    "apy": 3.2,
                    "tvl": 450000000,  # $450M
                    "risk_level": "LOW",
                    "minimum_deposit": 0.01,
                    "liquidity_score": 0.88,
                    "protocol_risk_score": 0.85,
                    "smart_contract_risk": 0.85,
                    "description": "ETH collateral earning on Compound"
                },
                {
                    "id": "lido_steth",
                    "protocol": "Lido",
                    "asset": "stETH",
                    "strategy": "Liquid Staking",
                    "apy": 3.8,
                    "tvl": 15200000000,  # $15.2B
                    "risk_level": "LOW",
                    "minimum_deposit": 0.01,
                    "liquidity_score": 0.92,
                    "protocol_risk_score": 0.88,
                    "smart_contract_risk": 0.87,
                    "description": "Ethereum staking rewards through Lido"
                },
                {
                    "id": "curve_3pool",
                    "protocol": "Curve",
                    "asset": "3CRV",
                    "strategy": "Stable LP",
                    "apy": 2.1,
                    "tvl": 680000000,  # $680M
                    "risk_level": "LOW",
                    "minimum_deposit": 100,
                    "liquidity_score": 0.85,
                    "protocol_risk_score": 0.82,
                    "smart_contract_risk": 0.82,
                    "description": "Stable coin liquidity provision on Curve"
                },
                {
                    "id": "uniswap_v3_usdc_eth",
                    "protocol": "Uniswap V3",
                    "asset": "USDC/ETH",
                    "strategy": "LP Concentrated",
                    "apy": 12.5,
                    "tvl": 320000000,  # $320M
                    "risk_level": "MEDIUM",
                    "minimum_deposit": 1000,
                    "liquidity_score": 0.78,
                    "protocol_risk_score": 0.85,
                    "smart_contract_risk": 0.80,
                    "description": "Concentrated liquidity provision USDC/ETH"
                },
                {
                    "id": "yearn_yvusdc",
                    "protocol": "Yearn",
                    "asset": "yvUSDC",
                    "strategy": "Yield Optimization",
                    "apy": 6.8,
                    "tvl": 125000000,  # $125M
                    "risk_level": "MEDIUM",
                    "minimum_deposit": 100,
                    "liquidity_score": 0.75,
                    "protocol_risk_score": 0.80,
                    "smart_contract_risk": 0.78,
                    "description": "Automated USDC yield farming via Yearn"
                }
            ]

            logger.info(f"Discovered {len(opportunities)} yield opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error discovering yield opportunities: {e}")
            return []

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

                # Risk assessment
                overall_risk_score = self._calculate_overall_risk_score(opp)

                # Calculate Sakura compatibility score
                sakura_score = self._calculate_sakura_score(opp, overall_risk_score)

                # Add computed fields
                enhanced_opp = {
                    **opp,
                    "sakura_score": sakura_score,
                    "overall_risk_score": overall_risk_score,
                    "projected_returns": self._calculate_projected_returns(opp['apy']),
                    "recommended_allocation": min(10.0, sakura_score * 12),  # Max 10% allocation
                    "analysis_timestamp": datetime.now().isoformat()
                }

                # Only include opportunities with good Sakura scores
                if sakura_score >= 0.6:
                    suitable.append(enhanced_opp)

            except Exception as e:
                logger.warning(f"Error filtering opportunity {opp.get('id', 'unknown')}: {e}")

        # Sort by Sakura score
        suitable.sort(key=lambda x: x['sakura_score'], reverse=True)
        return suitable[:8]  # Top 8 opportunities

    def _calculate_overall_risk_score(self, opportunity: Dict[str, Any]) -> float:
        """Calculate overall risk score for an opportunity."""
        try:
            # Weight different risk factors
            protocol_risk = opportunity.get('protocol_risk_score', 0.8)
            smart_contract_risk = opportunity.get('smart_contract_risk', 0.8)
            liquidity_score = opportunity.get('liquidity_score', 0.8)

            # TVL risk (higher TVL = lower risk)
            tvl_risk_score = min(1.0, opportunity['tvl'] / 1000000000)  # $1B = max score

            # APY risk (higher APY = higher risk)
            apy_risk_score = max(0.3, 1.0 - (opportunity['apy'] - 3) / 25)  # Higher APY reduces score

            # Weighted average
            overall_score = (
                protocol_risk * 0.25 +
                smart_contract_risk * 0.25 +
                liquidity_score * 0.20 +
                tvl_risk_score * 0.15 +
                apy_risk_score * 0.15
            )

            return round(overall_score, 3)

        except Exception:
            return 0.5

    def _calculate_sakura_score(self, opportunity: Dict[str, Any], risk_score: float) -> float:
        """Calculate Sakura compatibility score."""
        try:
            score = 0.0

            # Risk preference (40% weight) - Sakura prefers low risk
            if opportunity['risk_level'] == 'LOW':
                score += 0.4
            elif opportunity['risk_level'] == 'MEDIUM':
                score += 0.25
            else:
                score += 0.1

            # APY preference (25% weight) - Moderate yields preferred
            apy = opportunity['apy']
            if 3 <= apy <= 8:
                score += 0.25
            elif 8 < apy <= 15:
                score += 0.20
            else:
                score += 0.10

            # Liquidity preference (20% weight)
            liquidity_score = opportunity.get('liquidity_score', 0.5)
            score += liquidity_score * 0.20

            # Protocol maturity (15% weight)
            protocol = opportunity['protocol'].lower()
            if any(name in protocol for name in ['aave', 'compound', 'lido']):
                score += 0.15  # Established protocols
            elif any(name in protocol for name in ['curve', 'uniswap']):
                score += 0.12  # Well-known protocols
            else:
                score += 0.08  # Other protocols

            # Apply risk score multiplier
            score *= risk_score

            return round(min(1.0, score), 3)

        except Exception:
            return 0.5

    def _calculate_projected_returns(self, apy: float) -> Dict[str, float]:
        """Calculate projected returns for different time periods."""
        try:
            return {
                "monthly": round(apy / 12, 2),
                "quarterly": round(apy / 4, 2),
                "yearly": round(apy, 2)
            }
        except Exception:
            return {"monthly": 0.0, "quarterly": 0.0, "yearly": 0.0}

    async def _calculate_portfolio_allocation(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate optimal portfolio allocation."""
        try:
            if not opportunities:
                return {
                    "allocations": [],
                    "total_allocation": 0.0,
                    "expected_portfolio_apy": 0.0,
                    "diversification_score": 0.0
                }

            allocations = []
            total_score = sum(opp['sakura_score'] for opp in opportunities)
            total_allocation = 0.0
            weighted_apy = 0.0

            for opp in opportunities:
                # Calculate allocation based on score
                base_allocation = (opp['sakura_score'] / total_score) * 30  # Max 30% total in yield farming

                # Cap per protocol
                max_protocol_allocation = self.max_allocation_per_protocol * 100  # Convert to percentage
                capped_allocation = min(base_allocation, max_protocol_allocation)

                # Minimum threshold
                if capped_allocation >= 2.0:  # Minimum 2% to be meaningful
                    allocation = {
                        "opportunity_id": opp['id'],
                        "protocol": opp['protocol'],
                        "asset": opp['asset'],
                        "strategy": opp['strategy'],
                        "allocation_percentage": round(capped_allocation, 1),
                        "expected_apy": opp['apy'],
                        "risk_level": opp['risk_level'],
                        "sakura_score": opp['sakura_score']
                    }

                    allocations.append(allocation)
                    total_allocation += capped_allocation
                    weighted_apy += opp['apy'] * (capped_allocation / 100)

            # Calculate diversification score
            diversification_score = self._calculate_diversification_score(allocations)

            return {
                "allocations": allocations,
                "total_allocation": round(total_allocation, 1),
                "expected_portfolio_apy": round(weighted_apy, 2),
                "diversification_score": diversification_score,
                "allocation_strategy": "Conservative diversified yield farming",
                "rebalance_frequency": "Monthly"
            }

        except Exception as e:
            logger.error(f"Portfolio allocation calculation failed: {e}")
            return {
                "allocations": [],
                "total_allocation": 0.0,
                "expected_portfolio_apy": 0.0,
                "diversification_score": 0.0,
                "error": "Allocation calculation failed"
            }

    def _calculate_diversification_score(self, allocations: List[Dict[str, Any]]) -> float:
        """Calculate portfolio diversification score."""
        try:
            if not allocations:
                return 0.0

            # Protocol diversification
            protocols = set(alloc['protocol'] for alloc in allocations)
            protocol_score = min(1.0, len(protocols) / 4)  # Perfect score with 4+ protocols

            # Asset diversification
            assets = set(alloc['asset'] for alloc in allocations)
            asset_score = min(1.0, len(assets) / 3)  # Perfect score with 3+ assets

            # Strategy diversification
            strategies = set(alloc['strategy'] for alloc in allocations)
            strategy_score = min(1.0, len(strategies) / 3)  # Perfect score with 3+ strategies

            # Allocation concentration (avoid over-concentration)
            max_allocation = max(alloc['allocation_percentage'] for alloc in allocations)
            concentration_score = max(0.0, 1.0 - (max_allocation - 15) / 15)  # Penalize >15% allocations

            # Weighted diversification score
            diversification_score = (
                protocol_score * 0.3 +
                asset_score * 0.25 +
                strategy_score * 0.25 +
                concentration_score * 0.2
            )

            return round(diversification_score, 3)

        except Exception:
            return 0.5

    def _generate_risk_assessment(self, opportunities: List[Dict[str, Any]]) -> str:
        """Generate overall risk assessment."""
        try:
            if not opportunities:
                return "No opportunities available for risk assessment"

            risk_levels = [opp['risk_level'] for opp in opportunities]
            low_risk_count = risk_levels.count('LOW')
            medium_risk_count = risk_levels.count('MEDIUM')
            high_risk_count = risk_levels.count('HIGH')

            total_opportunities = len(opportunities)
            avg_apy = np.mean([opp['apy'] for opp in opportunities])
            avg_risk_score = np.mean([opp['overall_risk_score'] for opp in opportunities])

            if low_risk_count >= total_opportunities * 0.8:
                risk_category = "LOW"
                risk_description = "Portfolio dominated by low-risk, stable yield opportunities"
            elif (low_risk_count + medium_risk_count) >= total_opportunities * 0.9:
                risk_category = "MEDIUM"
                risk_description = "Balanced portfolio with conservative risk profile"
            else:
                risk_category = "ELEVATED"
                risk_description = "Higher risk opportunities present, consider reducing allocation"

            assessment = f"{risk_category} - {risk_description}. "
            assessment += f"Average APY: {avg_apy:.1f}%, Risk Score: {avg_risk_score:.2f}. "
            assessment += f"Distribution: {low_risk_count} low-risk, {medium_risk_count} medium-risk opportunities."

            return assessment

        except Exception:
            return "Risk assessment unavailable"


# Global service instance
_sakura_agent: Optional[SakuraAgent] = None


async def get_sakura_agent() -> SakuraAgent:
    """Get or create Sakura agent instance."""
    global _sakura_agent
    if _sakura_agent is None:
        _sakura_agent = SakuraAgent()
    return _sakura_agent