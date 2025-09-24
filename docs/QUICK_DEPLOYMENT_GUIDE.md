# Quick Deployment Guide

## Prerequisites

✅ **Foundry installed**
✅ **Python 3.9+**
✅ **Alchemy API key**
✅ **BaseScan API key**
✅ **MetaMask wallet with ETH on Base**

## 1. Contract Deployment

```bash
# Navigate to contracts directory
cd contracts

# Install dependencies
forge install OpenZeppelin/openzeppelin-contracts@v4.9.3

# Setup environment
cp .env.example .env
# Edit .env with your actual keys:
# PRIVATE_KEY=0x...
# ALCHEMY_API_KEY=...
# BASESCAN_API_KEY=...

# Deploy to Base Sepolia (testnet)
./deploy-virtuals-acp.sh

# Deploy to Base Mainnet (when ready)
SKIP_TESTNET=true ./deploy-virtuals-acp.sh
```

**Expected Output:**
```
✅ Base Sepolia deployment completed!
Contract address: 0x486426C26B357a415722dEBc19E9B6082c481176
```

## 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with deployed contract address:
# VIRTUALS_ACP_CONTRACT_ADDRESS=0x486426C26B357a415722dEBc19E9B6082c481176
# ALCHEMY_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
# BACKEND_PRIVATE_KEY=0x...

# Start the server
uvicorn app.main:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     VirtualsACP contract loaded at 0x486426C26B357a415722dEBc19E9B6082c481176
```

## 3. Verification

```bash
# Test the API
curl http://localhost:8001/

# Test unified endpoint
curl -X POST "http://localhost:8001/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "analyze",
    "payload": {"symbol": "ETH/USD"},
    "requestId": "test_001",
    "amount": 0.001,
    "currency": "ETH",
    "userWallet": "0x..."
  }'

# Run full example suite
cd examples && ./curl.sh
```

## 4. Production Deployment

### Option A: Local Tunnel (Quick)
```bash
# Install ngrok
npm install -g ngrok

# Create tunnel
ngrok http 8001

# Use the https URL in Virtuals dashboard
```

### Option B: Cloud Deployment (Recommended)

**Render.com:**
1. Connect GitHub repo
2. Set environment variables:
   - `VIRTUALS_ACP_CONTRACT_ADDRESS`
   - `ALCHEMY_RPC_URL`
   - `BACKEND_PRIVATE_KEY`
   - `CHAIN_ID=8453`
3. Deploy backend service

**Railway.app:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

## 5. Virtuals Platform Registration

1. **Create Virtuals Account**
   - Visit Virtuals platform
   - Connect wallet used for deployment

2. **Register Provider**
   - Add backend URL (https://your-backend.com)
   - Register three agents:
     - flow-yuki (market_analysis, futures_trading)
     - flow-sakura (yield_optimization, token_analysis)
     - flow-ryu (balanced_trading, trade_scanner)

3. **Set Webhook URL**
   - Point to: `https://your-backend.com/api/virtuals/request`

## 6. Testing & Graduation

```bash
# Test all agents
./examples/curl.sh

# Monitor logs
tail -f backend.log

# Check contract on BaseScan
# https://basescan.org/address/0x486426C26B357a415722dEBc19E9B6082c481176
```

**Graduation Requirements:**
- ✅ Contract deployed and verified
- ✅ Backend publicly accessible
- ✅ 3 consecutive successful requests
- ✅ 10 total successful requests

## Troubleshooting

**Contract deployment fails:**
```bash
# Check balance
cast balance --rpc-url base_sepolia $DEPLOYER_ADDRESS

# Retry with higher gas
GAS_LIMIT=5000000 ./deploy-virtuals-acp.sh
```

**Backend connection issues:**
```bash
# Test locally first
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Check environment variables
python -c "from app.config.settings import settings; print(settings.VIRTUALS_ACP_CONTRACT_ADDRESS)"
```

**Mock mode responses:**
- Backend runs in mock mode if environment variables missing
- Provides realistic responses for testing
- Contract interactions disabled until properly configured

---

🎯 **Total deployment time: ~15 minutes**