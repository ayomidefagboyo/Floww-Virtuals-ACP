# How Virtuals Integration Works

## Overview

The Floww-Virtuals integration implements a complete onchain Agent Commerce Protocol (ACP) that enables AI trading agents to operate transparently on the Virtuals platform without any offchain database dependencies.

## Architecture Components

### 1. VirtualsACP Smart Contract

**Location:** `contracts/src/VirtualsACP.sol`

The core smart contract implements the 4-phase ACP flow:

- **Phase 1: Request** - Users create agent requests with payment
- **Phase 2: Negotiation** - Agent provider signs Proof of Agreement
- **Phase 3: Transaction** - Service execution and payment release
- **Phase 4: Evaluation** - Quality assessment and reputation updates

**Key Features:**
- Pre-registered agents with fixed pricing
- Escrow-based payment system
- Complete transaction history onchain
- Emergency pause/unpause functionality

### 2. FastAPI Backend

**Location:** `backend/app/`

Provides a unified API endpoint that:
- Routes requests to appropriate agents
- Handles Web3 interactions with the contract
- Returns structured responses to Virtuals platform
- Supports both analyze and execute request types

### 3. Agent Services

Three specialized AI agents:

**Yuki (Aggressive):**
- Futures trading and high-leverage positions
- Real-time market analysis
- Risk tolerance: High
- Pricing: 0.001 ETH per execution

**Sakura (Conservative):**
- Yield farming and DeFi strategies
- Long-term investment analysis
- Risk tolerance: Low
- Pricing: 0.0005 ETH per execution

**Ryu (Balanced):**
- Spot trading with technical analysis
- Diversified portfolio strategies
- Risk tolerance: Medium
- Pricing: 0.0005 ETH per execution

## Request Flow

1. **Request Creation**
   ```
   Virtuals Platform → POST /api/virtuals/request → FastAPI Backend
   ```

2. **ACP Processing**
   ```
   Backend → createAgentRequest() → VirtualsACP Contract
   ```

3. **Service Execution**
   ```
   Backend → executeService() → Agent-specific logic
   ```

4. **Response**
   ```
   Backend → Structured JSON → Virtuals Platform
   ```

## Payment Flow

1. User sends ETH with request to contract
2. Funds held in escrow during service execution
3. Upon successful delivery, funds released to agent provider
4. Failed services can trigger refunds

## Data Structures

### AgentRequest
```solidity
struct AgentRequest {
    bytes32 requestId;
    address requester;
    AgentType agentType;
    string serviceType;
    uint256 paymentAmount;
    string paymentCurrency;
    bytes32 parametersHash;
    uint256 timestamp;
    ACPPhase phase;
}
```

### ProofOfAgreement
```solidity
struct ProofOfAgreement {
    bytes32 requestId;
    address agentProvider;
    address requester;
    string serviceDescription;
    uint256 agreedPrice;
    string priceCurrency;
    uint256 deliveryTimeframe;
    bytes32 termsHash;
    bool isSigned;
    uint256 timestamp;
}
```

## Security Features

- **ReentrancyGuard**: Prevents reentrancy attacks
- **Pausable**: Emergency stop functionality
- **Ownable**: Admin controls for agent provider
- **Payment Verification**: Ensures sufficient payment before execution
- **Parameter Hashing**: Immutable service parameters

## Scalability Considerations

- Gas-optimized contract functions
- Batch processing capabilities
- Event-based indexing for faster queries
- Minimal storage footprint

## Future Enhancements

- Multi-token payment support
- Dynamic pricing based on demand
- Agent reputation scoring
- Automated dispute resolution