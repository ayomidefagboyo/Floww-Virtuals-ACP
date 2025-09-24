"""
Virtuals ACP Adapter - Unified endpoint for Virtuals platform integration.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.virtuals_acp_service import get_virtuals_acp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/virtuals", tags=["Virtuals ACP"])


class VirtualsRequest(BaseModel):
    """Unified Virtuals request model."""
    agentId: str = Field(..., description="Agent ID (flow-yuki, flow-sakura, flow-ryu)")
    serviceName: str = Field(..., description="Service name")
    requestType: str = Field(..., description="Request type (analyze or execute)")
    payload: Dict[str, Any] = Field(..., description="Service-specific payload")
    requestId: str = Field(..., description="Unique request identifier")
    amount: float = Field(..., description="Payment amount in ETH")
    currency: str = Field(default="ETH", description="Payment currency")
    userWallet: str = Field(..., description="User wallet address")


class VirtualsResponse(BaseModel):
    """Unified Virtuals response model."""
    request_id: str
    agent_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    transaction_hash: Optional[str] = None
    estimated_pnl: Optional[float] = None


@router.post("/request", response_model=VirtualsResponse)
async def handle_virtuals_request(request: VirtualsRequest) -> VirtualsResponse:
    """
    Unified endpoint for Virtuals platform requests.

    Handles both analyze and execute requests for all Flow AI agents.
    """
    try:
        logger.info(f"Processing Virtuals request: {request.agentId} - {request.serviceName} - {request.requestType}")

        # Get the ACP service
        acp_service = get_virtuals_acp_service()

        # Route request based on type
        if request.requestType == "analyze":
            # For analyze requests, pass market_data in parameters
            parameters = {"market_data": request.payload}

            # Create ACP request
            create_result = await acp_service.create_request(
                agent_id=request.agentId,
                service_name=request.serviceName,
                request_type=request.requestType,
                payload=parameters,
                amount=request.amount,
                user_wallet=request.userWallet
            )

            if create_result["status"] != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to create ACP request: {create_result.get('error', 'Unknown error')}"
                )

            # Execute the analysis service
            execution_result = await acp_service.execute_service(
                request_id=create_result["request_id"],
                parameters=parameters
            )

            # Return unified response
            return VirtualsResponse(
                request_id=create_result["request_id"],
                agent_id=request.agentId,
                status=execution_result["status"],
                result=execution_result.get("result"),
                error_message=execution_result.get("error"),
                transaction_hash=create_result.get("transaction_hash")
            )

        elif request.requestType == "execute":
            # For execute requests, pass payload directly as parameters
            parameters = request.payload

            # Create ACP request
            create_result = await acp_service.create_request(
                agent_id=request.agentId,
                service_name=request.serviceName,
                request_type=request.requestType,
                payload=parameters,
                amount=request.amount,
                user_wallet=request.userWallet
            )

            if create_result["status"] != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to create ACP request: {create_result.get('error', 'Unknown error')}"
                )

            # Execute the service
            execution_result = await acp_service.execute_service(
                request_id=create_result["request_id"],
                parameters=parameters
            )

            # Extract estimated P&L if available
            estimated_pnl = None
            if execution_result.get("result") and "execution" in execution_result["result"]:
                estimated_pnl = execution_result["result"]["execution"].get("estimated_pnl")

            # Return unified response
            return VirtualsResponse(
                request_id=create_result["request_id"],
                agent_id=request.agentId,
                status=execution_result["status"],
                result=execution_result.get("result"),
                error_message=execution_result.get("error"),
                transaction_hash=create_result.get("transaction_hash"),
                estimated_pnl=estimated_pnl
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request type: {request.requestType}. Must be 'analyze' or 'execute'"
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing Virtuals request: {e}")
        return VirtualsResponse(
            request_id=request.requestId,
            agent_id=request.agentId,
            status="error",
            error_message=str(e)
        )


@router.get("/agents")
async def get_available_agents():
    """Get list of available Flow AI agents for Virtuals platform."""
    return {
        "agents": [
            {
                "agent_id": "flow-yuki",
                "name": "Yuki - Aggressive Trading",
                "description": "High-risk, high-reward futures trading agent",
                "pricing": {"type": "per_execution", "amount": "0.001", "currency": "ETH"},
                "services": ["market_analysis", "futures_trading"],
                "risk_level": "high"
            },
            {
                "agent_id": "flow-sakura",
                "name": "Sakura - Conservative Yield",
                "description": "Low-risk yield farming and DeFi strategies",
                "pricing": {"type": "per_execution", "amount": "0.0005", "currency": "ETH"},
                "services": ["yield_optimization", "token_analysis"],
                "risk_level": "low"
            },
            {
                "agent_id": "flow-ryu",
                "name": "Ryu - Balanced Trading",
                "description": "Moderate risk spot trading with AI analysis",
                "pricing": {"type": "per_execution", "amount": "0.0005", "currency": "ETH"},
                "services": ["balanced_trading", "trade_scanner"],
                "risk_level": "medium"
            }
        ],
        "platform": "virtuals",
        "network": "base",
        "total_agents": 3
    }


@router.get("/status")
async def get_integration_status():
    """Get Virtuals integration status."""
    acp_service = get_virtuals_acp_service()

    return {
        "platform": "virtuals",
        "integration_status": "active",
        "contract_deployed": acp_service.contract is not None,
        "contract_address": acp_service.contract_address,
        "network": "base",
        "agents_registered": 3,
        "services_available": [
            "market_analysis",
            "yield_optimization",
            "balanced_trading",
            "futures_trading",
            "token_analysis",
            "trade_scanner"
        ]
    }