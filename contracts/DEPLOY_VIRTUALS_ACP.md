# VirtualsACP Contract Deployment Guide

## Prerequisites

1. **Install Foundry**:
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Install OpenZeppelin Contracts**:
   ```bash
   forge install OpenZeppelin/openzeppelin-contracts@v4.9.3
   ```

3. **Setup Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

## Environment Variables

Create a `.env` file with:

```bash
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
ALCHEMY_API_KEY=YOUR_ALCHEMY_API_KEY_HERE
BASESCAN_API_KEY=YOUR_BASESCAN_API_KEY_HERE
```

### Getting API Keys

- **Alchemy API Key**: Get from [Alchemy Dashboard](https://dashboard.alchemy.com/)
- **BaseScan API Key**: Get from [BaseScan](https://basescan.org/apis)
- **Private Key**: Export from MetaMask (Account Details → Export Private Key)

## Deployment

### Option 1: Using the Deployment Script (Recommended)

```bash
./deploy-virtuals-acp.sh
```

This script will:
1. Deploy to Base Sepolia (testnet) first for testing
2. Ask for confirmation before deploying to Base Mainnet
3. Verify contracts on BaseScan automatically

### Option 2: Manual Deployment

**Deploy to Base Sepolia (Testnet):**
```bash
forge script script/DeployVirtualsACP.s.sol:DeployVirtualsACP \
    --rpc-url base_sepolia \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --etherscan-api-key $BASESCAN_API_KEY \
    --verify
```

**Deploy to Base Mainnet:**
```bash
forge script script/DeployVirtualsACP.s.sol:DeployVirtualsACP \
    --rpc-url base_mainnet \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --etherscan-api-key $BASESCAN_API_KEY \
    --verify
```

## Verification

After deployment, check your contracts on:
- **Base Sepolia**: https://sepolia.basescan.org/
- **Base Mainnet**: https://basescan.org/

## Contract Features

The deployed VirtualsACP contract includes:

### Pre-registered Agents
- **Yuki** (AgentType.YUKI): Aggressive futures trading - 0.001 ETH
- **Sakura** (AgentType.SAKURA): Conservative yield farming - 0.0005 ETH
- **Ryu** (AgentType.RYU): Balanced spot trading - 0.0005 ETH

### ACP Flow Functions
1. `createAgentRequest()` - Phase 1: Request
2. `signProofOfAgreement()` - Phase 2: Negotiation
3. `initiateTransaction()` - Phase 3: Transaction
4. `deliverService()` - Complete service delivery
5. `completeEvaluation()` - Phase 4: Evaluation

## Next Steps

1. Save the deployed contract address
2. Update your backend `.env` with `VIRTUALS_ACP_CONTRACT_ADDRESS`
3. Register services with Virtuals platform
4. Test the integration with sample requests

## Troubleshooting

- **"Insufficient payment"**: Ensure you send enough ETH for the agent type
- **"Agent not active"**: All agents are active by default after deployment
- **Verification failed**: Check your BaseScan API key and try manual verification