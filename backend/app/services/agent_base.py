"""
Base Agent Service - Reliability-First Architecture

This provides a common foundation for all trading agents with:
- Guaranteed response structure
- Built-in error handling and fallbacks
- Simplified external dependencies
- Consistent API interface
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent operational status."""
    ONLINE = "online"
    ANALYZING = "analyzing"
    OFFLINE = "offline"
    ERROR = "error"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class ActionType(Enum):
    """Trading action types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    AVOID = "AVOID"


@dataclass
class AgentResult:
    """Standardized agent result structure."""
    agent_id: str
    agent_name: str
    success: bool
    timestamp: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str = AgentStatus.ONLINE.value


@dataclass
class MarketData:
    """Basic market data structure."""
    symbol: str
    current_price: float
    price_change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    market_cap: Optional[float] = None


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
    bb_position: float = 0.5
    ema_20: float = 0.0
    ema_50: float = 0.0
    volume_sma_10: float = 0.0
    atr_14: float = 0.0


class BaseAgent(ABC):
    """
    Base agent class providing common functionality and reliability guarantees.

    All agents inherit from this to ensure:
    - Consistent response format
    - Error handling and fallbacks
    - Status management
    - Timeout protection
    """

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.status = AgentStatus.ONLINE
        self.last_activity = datetime.now()
        self.request_timeout = 30  # seconds

    @abstractmethod
    async def _execute_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the core analysis logic.
        Must be implemented by each agent.
        """
        pass

    async def execute(self, params: Dict[str, Any]) -> AgentResult:
        """
        Execute agent analysis with full error handling and timeouts.
        This is the main entry point for all agents.
        """
        self.last_activity = datetime.now()

        try:
            # Set status to analyzing
            self.status = AgentStatus.ANALYZING

            # Execute with timeout
            result_data = await asyncio.wait_for(
                self._execute_analysis(params),
                timeout=self.request_timeout
            )

            # Success response
            self.status = AgentStatus.ONLINE
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                success=True,
                timestamp=datetime.now().isoformat(),
                data=result_data,
                status=self.status.value
            )

        except asyncio.TimeoutError:
            logger.error(f"{self.agent_name} analysis timed out after {self.request_timeout}s")
            self.status = AgentStatus.ERROR
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                success=False,
                timestamp=datetime.now().isoformat(),
                error=f"Analysis timed out after {self.request_timeout} seconds",
                status=self.status.value
            )

        except Exception as e:
            logger.error(f"{self.agent_name} analysis failed: {e}")
            self.status = AgentStatus.ERROR
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                success=False,
                timestamp=datetime.now().isoformat(),
                error=str(e),
                status=self.status.value
            )

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "status": self.status.value,
            "last_activity": self.last_activity.isoformat(),
            "capabilities": self.get_capabilities()
        }

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass

    def calculate_basic_technical_score(self, indicators: TechnicalIndicators) -> float:
        """Calculate a basic technical score from indicators."""
        try:
            score = 0.0

            # RSI component (30% weight)
            if 30 <= indicators.rsi_14 <= 70:
                rsi_score = 0.3
            elif indicators.rsi_14 < 20 or indicators.rsi_14 > 80:
                rsi_score = 0.1  # Extreme levels
            else:
                rsi_score = 0.2
            score += rsi_score

            # MACD component (25% weight)
            if indicators.macd_line > indicators.macd_signal:
                macd_score = 0.25
            else:
                macd_score = 0.15
            score += macd_score

            # Bollinger Band position (25% weight)
            if 0.2 <= indicators.bb_position <= 0.8:
                bb_score = 0.25
            else:
                bb_score = 0.15
            score += bb_score

            # EMA trend (20% weight)
            if indicators.ema_20 > indicators.ema_50:
                trend_score = 0.2
            else:
                trend_score = 0.1
            score += trend_score

            return min(1.0, score)

        except Exception as e:
            logger.warning(f"Technical score calculation failed: {e}")
            return 0.5  # Default neutral score

    def determine_risk_level(self, volatility: float, volume: float) -> RiskLevel:
        """Determine risk level based on market conditions."""
        try:
            risk_factors = 0

            # Volatility risk
            if volatility > 0.15:  # 15%+ daily volatility
                risk_factors += 2
            elif volatility > 0.08:  # 8%+ daily volatility
                risk_factors += 1

            # Liquidity risk
            if volume < 100000:  # Low volume
                risk_factors += 2
            elif volume < 1000000:  # Medium volume
                risk_factors += 1

            # Determine overall risk
            if risk_factors >= 3:
                return RiskLevel.HIGH
            elif risk_factors >= 1:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW

        except Exception:
            return RiskLevel.MEDIUM  # Default fallback

    def generate_fallback_response(self, symbol: str, action: ActionType = ActionType.HOLD) -> Dict[str, Any]:
        """Generate a safe fallback response when analysis fails."""
        return {
            "symbol": symbol,
            "action": action.value,
            "confidence": 0.5,
            "reasoning": f"{self.agent_name} analysis unavailable - using conservative fallback",
            "risk_level": RiskLevel.MEDIUM.value,
            "timestamp": datetime.now().isoformat(),
            "fallback_mode": True
        }