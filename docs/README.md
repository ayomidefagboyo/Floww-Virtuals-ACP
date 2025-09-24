# Floww Virtuals ACP Integration

Floww AI agents integration with the Virtuals Agent Commerce Protocol (ACP) for the Ethereum AI Hackathon. This repository contains a complete onchain agent commerce system with three specialized AI trading agents deployed on Base network.

## Platform Overview

Floww provides three AI trading agents that integrate with the Virtuals platform through a custom ACP implementation:

- **Yuki** 🔥 - Futures trading agent that generate 5 best trading opportinities 
- **Sakura** 🌸 - Conservative yield farming and DeFi strategies 
- **Ryu** ⚖️ - Token Analysis AI Agent

All agents operate through a fully onchain ACP protocol with no offchain database dependencies.

## 🚀 Quick Start

### 1. Deploy the Smart Contract

```bash
cd contracts
cp .env.example .env
# Edit .env with your keys
./deploy-virtuals-acp.sh
```

### 2. Run the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your deployed contract address
uvicorn app.main:app --reload
```

### 3. Test the Integration

```bash
cd examples
./curl.sh
```

## 📡 Unified API Endpoint

### POST /api/virtuals/request

**Request:**
```json
{
  "agentId": "flow-yuki|flow-sakura|flow-ryu",
  "serviceName": "market_analysis|yield_optimization|balanced_trading|futures_trading|token_analysis|trade_scanner",
  "requestType": "analyze|execute",
  "payload": {
    "symbol": "ETH/USD",
    "amount": 1000,
    "strategy": "aggressive"
  },
  "requestId": "unique-request-id",
  "amount": 0.001,
  "currency": "ETH",
  "userWallet": "0x..."
}
```

**Response:**
```json
{
  "request_id": "0x...",
  "agent_id": "flow-yuki",
  "status": "success",
  "result": {
    "analysis": {
      "trend": "bullish",
      "confidence": 0.85,
      "recommended_action": "buy"
    }
  },
  "transaction_hash": "0x...",
  "estimated_pnl": 125.50
}
```

## 📋 Example Usage

### Market Analysis (Yuki)
```bash
curl -X POST "http://localhost:8000/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "analyze",
    "payload": {
      "symbol": "ETH/USD",
      "timeframe": "1h"
    },
    "requestId": "req_001",
    "amount": 0.001,
    "currency": "ETH",
    "userWallet": "0x..."
  }'
```

### Yield Optimization (Sakura)
```bash
curl -X POST "http://localhost:8000/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-sakura",
    "serviceName": "yield_optimization",
    "requestType": "execute",
    "payload": {
      "amount": 1000,
      "token": "USDC",
      "strategy": "conservative"
    },
    "requestId": "req_002",
    "amount": 0.0005,
    "currency": "ETH",
    "userWallet": "0x..."
  }'
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Virtuals        │    │ Floww Backend    │    │ VirtualsACP     │
│ Platform        │◄──►│ (FastAPI)        │◄──►│ Smart Contract  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼─────────┐
                       │ Agent Services   │
                       │ • Yuki (Futures) │
                       │ • Sakura (Yield) │
                       │ • Ryu (Balanced) │
                       └──────────────────┘
```

## 🔧 Local Development

**Requirements:**
- Python 3.9+
- Node.js (for Foundry)
- Foundry

**Setup:**
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Clone and setup
git clone <repo-url>
cd Floww-Virtuals-ACP

# Deploy contract
cd contracts && ./deploy-virtuals-acp.sh

# Run backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📝 Environment Variables

**Backend (.env):**
```bash
VIRTUALS_ACP_CONTRACT_ADDRESS=0x486426C26B357a415722dEBc19E9B6082c481176
ALCHEMY_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
BACKEND_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
CHAIN_ID=8453
```

**Contracts (.env):**
```bash
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
ALCHEMY_API_KEY=YOUR_ALCHEMY_KEY
BASESCAN_API_KEY=YOUR_BASESCAN_KEY
```

## 🌐 Deployed Addresses

- **Base Sepolia**: `0x486426C26B357a415722dEBc19E9B6082c481176`
- **Base Mainnet**: TBD

## 🔍 Additional Endpoints

- `GET /` - Service info and available endpoints
- `GET /api/virtuals/agents` - List all available agents
- `GET /api/virtuals/status` - Integration status
- `GET /health` - Health check

## 📚 Documentation

- [HOW_VIRTUALS_INTEGRATION_WORKS.md](docs/HOW_VIRTUALS_INTEGRATION_WORKS.md) - Technical details
- [QUICK_DEPLOYMENT_GUIDE.md](docs/QUICK_DEPLOYMENT_GUIDE.md) - Deployment instructions
- [contracts/DEPLOY_VIRTUALS_ACP.md](contracts/DEPLOY_VIRTUALS_ACP.md) - Contract deployment

## 🎪 Demo

Run the example script to see all agents in action:
```bash
cd examples && ./curl.sh
```

This will demonstrate:
- Market analysis with Yuki (futures trading)
- Yield optimization with Sakura (DeFi strategies)
- Balanced trading with Ryu (spot trading)

## 🔒 Security Notes

- Never commit `.env` files
- Use separate keys for testnet and mainnet
- All transactions are signed and verified onchain
- No private keys or secrets in this repository

---

Built for the **Virtuals Ethereum AI Hackathon** 🏆
