# Virtuals ACP Smart Contracts

## Overview

This directory contains the smart contract implementation for the Virtuals Agent Commerce Protocol (ACP), enabling onchain agent commerce with Flow's AI trading agents.

## Architecture

### VirtualsACP.sol
**Main ACP Protocol Contract** - implements the 4-phase agent commerce protocol.

**Core Features:**
- **Phase 1**: Request Creation - Users create service requests with ETH payment
- **Phase 2**: Proof of Agreement - Agents sign service agreements onchain
- **Phase 3**: Transaction Initiation - Payment escrow and service execution
- **Phase 4**: Service Delivery - Results delivery and payment release

**Supported Agents:**
- **Yuki (0)**: Aggressive trading with futures analysis
- **Sakura (1)**: Conservative yield farming with Pendle
- **Ryu (2)**: Balanced spot trading with analysis cards

**Core Functions:**
```solidity
function createAgentRequest(
    AgentType agentType,
    string memory serviceType,
    bytes32 parametersHash
) external payable returns (bytes32 requestId)

function signProofOfAgreement(
    bytes32 requestId,
    string memory serviceDescription,
    uint256 deliveryTimeframe,
    bytes32 termsHash
) external

function deliverService(
    bytes32 requestId,
    bool success,
    string memory result
) external
```

## Service Mapping

### Yuki Agent (AgentType.YUKI)
- **market_analysis**: Technical analysis with AI reasoning
- **futures_trading**: High-risk trading signals and execution
- **Pricing**: 0.001 ETH per execution

### Sakura Agent (AgentType.SAKURA)
- **yield_optimization**: DeFi yield farming strategies
- **pendle_yield**: Pendle protocol yield opportunities
- **Pricing**: 0.0005 ETH per execution

### Ryu Agent (AgentType.RYU)
- **token_analysis**: Professional token analysis cards
- **balanced_trading**: Moderate risk trading strategies
- **Pricing**: 0.0005 ETH per execution

## Network Configuration

### Base Sepolia (Testnet)
- **Chain ID**: 84532
- **RPC**: https://base-sepolia.g.alchemy.com/v2/YOUR_KEY
- **Contract**: Deployed via deployment script

### Base Mainnet (Production)
- **Chain ID**: 8453
- **RPC**: https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
- **Contract**: TBD

## Deployment

### Prerequisites
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts@v4.9.3
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your values:
# PRIVATE_KEY=0x...
# ALCHEMY_API_KEY=...
# BASESCAN_API_KEY=...
```

### Deploy to Testnet
```bash
# Deploy to Base Sepolia
./deploy-virtuals-acp.sh
```

### Deploy to Mainnet
```bash
# Deploy to Base Mainnet
SKIP_TESTNET=true ./deploy-virtuals-acp.sh
```

## Testing

### Run Contract Tests
```bash
# Run full test suite
forge test

# Run with verbose output
forge test -vvv

# Test specific contract
forge test --match-contract VirtualsACP
```

### Run Test Script
```bash
# Run comprehensive test script
./test.sh
```

## Integration

### API Integration
The contracts integrate with the Virtuals ACP backend service:
- **Backend**: Handles agent request routing
- **Smart Contract**: Manages payment escrow and service delivery
- **Agents**: Execute real trading/analysis functionality

### Request Flow
1. **User Request**: Creates request via API (`/api/virtuals/request`)
2. **Contract Call**: Backend calls `createAgentRequest()`
3. **Agent Execution**: Functional agents process the request
4. **Service Delivery**: Results delivered via `deliverService()`
5. **Payment Release**: ETH released to agent on successful completion

## Security Features

- **Payment Escrow**: ETH held in contract until service completion
- **Agent Authentication**: Only registered agents can deliver services
- **Request Validation**: Parameters hashed and verified onchain
- **Reentrancy Protection**: Standard OpenZeppelin guards
- **Access Controls**: Owner-only admin functions

## Development Status

### ✅ Completed
- [x] Core ACP protocol implementation
- [x] Agent registration system
- [x] Payment escrow mechanism
- [x] Service delivery validation
- [x] Base network deployment scripts
- [x] Integration with functional agents

### 📋 Future Enhancements
- [ ] Multi-token payment support
- [ ] Agent reputation system
- [ ] Dispute resolution mechanism
- [ ] Advanced service verification

## Example Usage

### JavaScript/TypeScript
```javascript
import { ethers } from 'ethers';

const contract = new ethers.Contract(
    VIRTUALS_ACP_ADDRESS,
    ACP_ABI,
    signer
);

// Create request for Yuki market analysis
const tx = await contract.createAgentRequest(
    0, // AgentType.YUKI
    "market_analysis",
    parametersHash,
    { value: ethers.utils.parseEther("0.001") }
);
```

### cURL API
```bash
curl -X POST "http://localhost:8001/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "analyze",
    "payload": {"symbol": "BTC"},
    "requestId": "test_001",
    "amount": 0.001,
    "userWallet": "0x..."
  }'
```

## Support

For issues or questions:
- Check deployment logs in `deployments/`
- Review contract events on BaseScan
- Test with local development environment first
- Ensure proper environment configuration

---

**Built for the Virtuals Ethereum AI Hackathon**
Implementing onchain agent commerce with real AI functionality.