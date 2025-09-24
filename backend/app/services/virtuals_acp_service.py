"""
Virtuals Agent Commerce Protocol (ACP) Integration Service

Handles Web3 interactions with the deployed VirtualsACP contract.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)


@dataclass
class ACPRequest:
    """ACP Request structure."""
    request_id: str
    requester: str
    agent_type: str
    service_type: str
    payment_amount: float
    payment_currency: str
    parameters: Dict[str, Any]


class VirtualsACPService:
    """Service for interacting with VirtualsACP smart contract."""

    def __init__(self):
        """Initialize the ACP service."""
        self.w3 = None
        self.contract = None
        self.account = None
        self.contract_address = None

        # Initialize if environment variables are present
        if self._has_required_env_vars():
            self._setup_web3()
        else:
            logger.warning("VirtualsACP service running in mock mode - missing environment variables")

    def _has_required_env_vars(self) -> bool:
        """Check if required environment variables are present."""
        return all([
            os.getenv('VIRTUALS_ACP_CONTRACT_ADDRESS'),
            os.getenv('ALCHEMY_RPC_URL'),
            os.getenv('BACKEND_PRIVATE_KEY')
        ])

    def _setup_web3(self):
        """Setup Web3 connection to Base network."""
        try:
            # Connect to Base network via Alchemy
            rpc_url = os.getenv('ALCHEMY_RPC_URL')
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not self.w3.is_connected():
                raise Exception("Failed to connect to Base network")

            # Setup account
            private_key = os.getenv('BACKEND_PRIVATE_KEY')
            self.account = Account.from_key(private_key)

            # Load contract
            self._load_contract()

            logger.info(f"Web3 connection established - account: {self.account.address}")

        except Exception as e:
            logger.error(f"Error setting up Web3: {e}")
            raise

    def _load_contract(self):
        """Load VirtualsACP contract."""
        try:
            # Contract ABI (key functions only)
            contract_abi = [
                {
                    "inputs": [
                        {"name": "agentType", "type": "uint8"},
                        {"name": "serviceType", "type": "string"},
                        {"name": "parametersHash", "type": "bytes32"}
                    ],
                    "name": "createAgentRequest",
                    "outputs": [{"name": "", "type": "bytes32"}],
                    "stateMutability": "payable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"name": "requestId", "type": "bytes32"},
                        {"name": "serviceDescription", "type": "string"},
                        {"name": "deliveryTimeframe", "type": "uint256"},
                        {"name": "termsHash", "type": "bytes32"}
                    ],
                    "name": "signProofOfAgreement",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "requestId", "type": "bytes32"}],
                    "name": "initiateTransaction",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"name": "requestId", "type": "bytes32"},
                        {"name": "success", "type": "bool"},
                        {"name": "result", "type": "string"}
                    ],
                    "name": "deliverService",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]

            self.contract_address = os.getenv('VIRTUALS_ACP_CONTRACT_ADDRESS')
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=contract_abi
            )

            logger.info(f"VirtualsACP contract loaded at {self.contract_address}")

        except Exception as e:
            logger.error(f"Error loading contract: {e}")
            raise

    async def register_service(self, agent_id: str, service_name: str, pricing: Dict[str, Any]) -> bool:
        """Register a service with the ACP (services are pre-registered in contract)."""
        if not self.contract:
            logger.info(f"Mock: Registering service {service_name} for agent {agent_id}")
            return True

        try:
            # Services are pre-registered in the contract constructor
            # This function acknowledges registration
            logger.info(f"Service {service_name} for agent {agent_id} is pre-registered in contract")
            return True

        except Exception as e:
            logger.error(f"Error registering service: {e}")
            return False

    async def create_request(
        self,
        agent_id: str,
        service_name: str,
        request_type: str,
        payload: Dict[str, Any],
        amount: float,
        user_wallet: str
    ) -> Dict[str, Any]:
        """Create an ACP request."""
        if not self.contract:
            # Mock response for development
            return {
                "request_id": f"mock_request_{agent_id}_{service_name}",
                "transaction_hash": "0xmocked_transaction_hash",
                "status": "success"
            }

        try:
            # Map agent_id to agent type enum
            agent_type = self._get_agent_type_enum(agent_id)

            # Hash parameters
            parameters_json = json.dumps(payload, sort_keys=True)
            parameters_hash = self.w3.keccak(text=parameters_json)

            # Build transaction
            transaction = self.contract.functions.createAgentRequest(
                agent_type,
                request_type,
                parameters_hash
            ).build_transaction({
                'from': self.account.address,
                'value': self.w3.to_wei(amount, 'ether'),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })

            # Sign and send transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                request_id = self._extract_request_id_from_receipt(receipt)
                return {
                    "request_id": request_id,
                    "transaction_hash": tx_hash.hex(),
                    "status": "success"
                }
            else:
                return {
                    "request_id": None,
                    "transaction_hash": tx_hash.hex(),
                    "status": "failed"
                }

        except Exception as e:
            logger.error(f"Error creating request: {e}")
            return {
                "request_id": None,
                "transaction_hash": None,
                "status": "error",
                "error": str(e)
            }

    async def execute_service(self, request_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a service (mock implementation for hackathon demo)."""
        try:
            # Mock service execution based on parameters
            if "market_data" in parameters:
                # Market analysis service
                result = {
                    "analysis": {
                        "trend": "bullish",
                        "confidence": 0.85,
                        "recommended_action": "buy",
                        "price_target": "$2,450",
                        "risk_level": "medium"
                    },
                    "indicators": {
                        "rsi": 65.2,
                        "macd": "bullish_crossover",
                        "bollinger_position": "upper_band"
                    }
                }
            else:
                # Generic execution result
                result = {
                    "execution": {
                        "status": "completed",
                        "transactions": 1,
                        "estimated_pnl": 125.50,
                        "gas_used": "0.002 ETH"
                    }
                }

            return {
                "request_id": request_id,
                "status": "success",
                "result": result,
                "completed_at": "2024-01-01T12:00:00Z"
            }

        except Exception as e:
            logger.error(f"Error executing service: {e}")
            return {
                "request_id": request_id,
                "status": "error",
                "error": str(e)
            }

    def _get_agent_type_enum(self, agent_id: str) -> int:
        """Convert agent ID to contract enum value."""
        agent_map = {
            'flow-yuki': 0,    # YUKI
            'flow-sakura': 1,  # SAKURA
            'flow-ryu': 2      # RYU
        }
        return agent_map.get(agent_id, 0)

    def _extract_request_id_from_receipt(self, receipt) -> str:
        """Extract request ID from transaction receipt."""
        # In a full implementation, this would parse the event logs
        # For now, return the transaction hash as request ID
        return receipt.transactionHash.hex()


# Global service instance
_virtuals_acp_service: Optional[VirtualsACPService] = None


def get_virtuals_acp_service() -> VirtualsACPService:
    """Get or create Virtuals ACP service instance."""
    global _virtuals_acp_service

    if _virtuals_acp_service is None:
        _virtuals_acp_service = VirtualsACPService()

    return _virtuals_acp_service