"""
Virtuals Agent Router - Routes requests to functional agent implementations.

This service acts as a middleware layer that routes Virtuals platform requests
to the appropriate functional agent implementations based on the actual
floww3.0 architecture.
"""

import logging
from typing import Dict, Any, Optional
from app.services.yuki_agent_service import get_yuki_agent_service
from app.services.ryu_agent_service import get_ryu_agent_service
from app.services.sakura_agent_service import get_sakura_agent_service

logger = logging.getLogger(__name__)


class VirtualsAgentRouter:
    """Routes Virtuals requests to appropriate functional agents."""

    def __init__(self):
        logger.info("Virtuals Agent Router initialized - routing to functional agents")

    async def route_request(
        self,
        agent_id: str,
        service_name: str,
        request_type: str,
        payload: Dict[str, Any],
        amount: float = 0.001
    ) -> Dict[str, Any]:
        """
        Route request to appropriate agent based on agent_id and service.

        This replaces the mock implementations with functional agent calls.
        """
        try:
            logger.info(f"Routing request: {agent_id} -> {service_name} ({request_type})")

            # Route to Yuki agent (Trade Scanner)
            if agent_id == "flow-yuki":
                return await self._route_to_yuki(service_name, request_type, payload, amount)

            # Route to Ryu agent (Token Analysis Cards)
            elif agent_id == "flow-ryu":
                return await self._route_to_ryu(service_name, request_type, payload, amount)

            # Route to Sakura agent (Pendle Yield Farming)
            elif agent_id == "flow-sakura":
                return await self._route_to_sakura(service_name, request_type, payload, amount)

            else:
                return {
                    "status": "error",
                    "error": f"Unknown agent ID: {agent_id}",
                    "result": None
                }

        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return {
                "status": "error",
                "error": f"Routing failed: {str(e)}",
                "result": None
            }

    async def _route_to_yuki(
        self,
        service_name: str,
        request_type: str,
        payload: Dict[str, Any],
        amount: float
    ) -> Dict[str, Any]:
        """Route to Yuki agent (Trade Scanner functionality)."""
        try:
            yuki_service = await get_yuki_agent_service()

            if service_name == "market_analysis":
                if request_type == "analyze":
                    symbol = payload.get("symbol", "BTC")
                    result = await yuki_service.analyze_specific_token(symbol)
                    return {
                        "status": "success" if not result.get("error") else "error",
                        "result": {
                            "analysis": result.get("analysis"),
                            "analysis_type": "yuki_trade_scanner",
                            "agent": "Yuki (Trade Scanner)"
                        },
                        "error": result.get("error")
                    }
                elif request_type == "execute":
                    symbol = payload.get("symbol", "BTC")
                    result = await yuki_service.execute_trade_analysis(symbol, amount)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("trade_execution"),
                            "analysis_type": "yuki_trade_execution",
                            "agent": "Yuki (Trade Scanner)"
                        },
                        "error": result.get("error")
                    }

            elif service_name == "futures_trading":
                if request_type == "scan":
                    result = await yuki_service.scan_market_opportunities()
                    return {
                        "status": "success" if not result.get("error") else "error",
                        "result": {
                            "scan": result.get("scan_results"),
                            "analysis_type": "yuki_market_scan",
                            "agent": "Yuki (Trade Scanner)"
                        },
                        "error": result.get("error")
                    }
                elif request_type == "execute":
                    symbol = payload.get("symbol", "BTC")
                    result = await yuki_service.execute_trade_analysis(symbol, amount)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("trade_execution"),
                            "analysis_type": "yuki_trade_execution",
                            "agent": "Yuki (Trade Scanner)"
                        },
                        "error": result.get("error")
                    }

            return {
                "status": "error",
                "error": f"Unknown service: {service_name}",
                "result": None
            }

        except Exception as e:
            logger.error(f"Error in Yuki routing: {e}")
            return {
                "status": "error",
                "error": f"Yuki agent error: {str(e)}",
                "result": None
            }

    async def _route_to_ryu(
        self,
        service_name: str,
        request_type: str,
        payload: Dict[str, Any],
        amount: float
    ) -> Dict[str, Any]:
        """Route to Ryu agent (Token Analysis Card functionality)."""
        try:
            ryu_service = await get_ryu_agent_service()

            if service_name == "token_analysis":
                if request_type == "analyze":
                    symbol = payload.get("symbol", "ETH")
                    risk_tolerance = payload.get("risk_tolerance", "medium")
                    time_horizon = payload.get("time_horizon", "medium")
                    result = await ryu_service.generate_token_analysis_card(symbol, risk_tolerance, time_horizon)
                    return {
                        "status": "success" if not result.get("error") else "error",
                        "result": {
                            "analysis": result.get("analysis_card"),
                            "analysis_type": "ryu_token_analysis_card",
                            "agent": "Ryu (Token Analysis)"
                        },
                        "error": result.get("error")
                    }
                elif request_type == "execute":
                    symbol = payload.get("symbol", "ETH")
                    risk_tolerance = payload.get("risk_tolerance", "medium")
                    time_horizon = payload.get("time_horizon", "medium")
                    result = await ryu_service.execute_token_analysis(symbol, amount, risk_tolerance, time_horizon)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("token_analysis"),
                            "analysis_type": "ryu_token_execution",
                            "agent": "Ryu (Token Analysis)"
                        },
                        "error": result.get("error")
                    }

            elif service_name == "balanced_trading":
                if request_type == "scan":
                    symbols = payload.get("symbols", ["ETH", "BTC", "SOL"])
                    risk_tolerance = payload.get("risk_tolerance", "medium")
                    # Generate analysis cards for multiple tokens
                    scan_results = []
                    for symbol in symbols:
                        card_result = await ryu_service.generate_token_analysis_card(symbol, risk_tolerance)
                        if not card_result.get("error"):
                            scan_results.append({
                                "symbol": symbol,
                                "analysis_card": card_result["analysis_card"]
                            })
                    return {
                        "status": "success",
                        "result": {
                            "scan": scan_results,
                            "total_analyzed": len(scan_results),
                            "analysis_type": "ryu_multi_token_scan",
                            "agent": "Ryu (Token Analysis)"
                        },
                        "error": None
                    }
                elif request_type == "execute":
                    symbol = payload.get("symbol", "ETH")
                    result = await ryu_service.execute_token_analysis(symbol, amount)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("token_analysis"),
                            "analysis_type": "ryu_token_execution",
                            "agent": "Ryu (Token Analysis)"
                        },
                        "error": result.get("error")
                    }

            return {
                "status": "error",
                "error": f"Unknown service: {service_name}",
                "result": None
            }

        except Exception as e:
            logger.error(f"Error in Ryu routing: {e}")
            return {
                "status": "error",
                "error": f"Ryu agent error: {str(e)}",
                "result": None
            }

    async def _route_to_sakura(
        self,
        service_name: str,
        request_type: str,
        payload: Dict[str, Any],
        amount: float
    ) -> Dict[str, Any]:
        """Route to Sakura agent (Pendle Yield Farming functionality)."""
        try:
            sakura_service = await get_sakura_agent_service()

            if service_name == "yield_optimization":
                if request_type == "analyze":
                    result = await sakura_service.analyze_yield_opportunities()
                    return {
                        "status": "success" if not result.get("error") else "error",
                        "result": {
                            "analysis": result.get("analysis"),
                            "analysis_type": "sakura_yield_analysis",
                            "agent": "Sakura (Yield Farming)"
                        },
                        "error": result.get("error")
                    }
                elif request_type == "execute":
                    result = await sakura_service.execute_yield_strategy(amount)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("yield_strategy"),
                            "analysis_type": "sakura_yield_execution",
                            "agent": "Sakura (Yield Farming)"
                        },
                        "error": result.get("error")
                    }

            elif service_name == "pendle_yield":
                if request_type == "scan":
                    focus_assets = payload.get("focus_assets", ["ETH", "USDC", "stETH"])
                    result = await sakura_service.scan_yield_markets(focus_assets)
                    return {
                        "status": "success" if not result.get("error") else "error",
                        "result": {
                            "scan": result.get("scan_results"),
                            "analysis_type": "sakura_yield_scan",
                            "agent": "Sakura (Yield Farming)"
                        },
                        "error": result.get("error")
                    }
                elif request_type == "execute":
                    result = await sakura_service.execute_yield_strategy(amount)
                    return {
                        "status": "success" if result.get("success") else "error",
                        "result": {
                            "execution": result.get("yield_strategy"),
                            "analysis_type": "sakura_yield_execution",
                            "agent": "Sakura (Yield Farming)"
                        },
                        "error": result.get("error")
                    }

            return {
                "status": "error",
                "error": f"Unknown service: {service_name}",
                "result": None
            }

        except Exception as e:
            logger.error(f"Error in Sakura routing: {e}")
            return {
                "status": "error",
                "error": f"Sakura agent error: {str(e)}",
                "result": None
            }


# Global router instance
_virtuals_agent_router: Optional[VirtualsAgentRouter] = None


def get_virtuals_agent_router() -> VirtualsAgentRouter:
    """Get or create Virtuals agent router instance."""
    global _virtuals_agent_router

    if _virtuals_agent_router is None:
        _virtuals_agent_router = VirtualsAgentRouter()

    return _virtuals_agent_router