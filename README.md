# Flow AI Agents - Virtuals ACP Integration

## Overview

This repository contains the integration of Flow's AI trading agents with the Virtuals Agent Commerce Protocol (ACP) for the Virtuals Ethereum AI Hackathon. The system provides onchain agent commerce through a 4-phase protocol enabling decentralized AI agent services on Base network.

## Architecture

### Agent Commerce Protocol (ACP)
- **Phase 1**: Request Creation - Users create service requests with ETH payment
- **Phase 2**: Proof of Agreement - Agents sign service agreements onchain
- **Phase 3**: Transaction Initiation - Payment escrow and service execution
- **Phase 4**: Service Delivery - Results delivery and payment release

### Available Agents

#### 🗲 Yuki - Aggressive Trading Agent
- **Specialty**: High-risk futures trading and market scanning
- **Technology**: Unified Signal Generator with 15+ technical indicators
- **Services**: Market analysis, futures trading signals, trade execution
- **Pricing**: 0.001 ETH per execution
- **Risk Level**: HIGH
- **Data Sources**: Live market data, technical analysis, AI reasoning with Claude API

#### 🌸 Sakura - Conservative Yield Agent
- **Specialty**: Low-risk yield farming and DeFi strategies
- **Technology**: Pendle Protocol integration for fixed yield opportunities
- **Services**: Yield optimization, Pendle market scanning, portfolio allocation
- **Pricing**: 0.0005 ETH per execution
- **Risk Level**: LOW
- **Data Sources**: Pendle markets, DeFi protocols, yield analytics

#### 🐉 Ryu - Balanced Trading Agent
- **Specialty**: Moderate risk spot trading with comprehensive analysis
- **Technology**: Token Analysis Card system with multi-factor scoring
- **Services**: Token analysis cards, balanced trading strategies, risk assessment
- **Pricing**: 0.0005 ETH per execution
- **Risk Level**: MEDIUM
- **Data Sources**: Technical analysis, market sentiment, fundamental analysis

## Functional Implementations

### Yuki Agent - Trade Scanner
**Based on Unified Signal Generator from floww3.0:**
- **Technical Analysis**: RSI, MACD, Bollinger Bands, momentum scoring
- **Market Discovery**: Scans entire crypto market for opportunities
- **AI Decision Making**: Claude API integration for intelligent reasoning
- **Signal Generation**: Professional trading signals with price targets
- **Risk Management**: Dynamic position sizing and stop-loss calculation

**Key Features:**
- 15+ technical indicators with real-time calculation
- AI-powered reasoning for trade decisions
- Market opportunity scoring and ranking
- Professional signal formatting with confidence levels

### Ryu Agent - Token Analysis Cards
**Based on Token Analysis Card API from floww3.0:**
- **Multi-factor Analysis**: Technical (35%), Fundamental (25%), Momentum (25%), Sentiment (15%)
- **Professional Formatting**: Comprehensive analysis cards with trade setup details
- **Dynamic Risk Assessment**: Adaptive risk management based on market conditions
- **Execution Strategy**: Detailed entry/exit strategies with price targets

**Key Features:**
- Professional analysis card formatting
- Multi-timeframe analysis support
- Risk-adjusted position sizing
- Alternative scenario planning

### Sakura Agent - Pendle Yield Farming
**Based on Pendle Service integration from floww3.0:**
- **Pendle Markets**: PT/YT market analysis with yield optimization
- **Conservative Strategy**: Focus on stable yield with risk assessment
- **Portfolio Allocation**: Multi-asset diversification with safety buffers
- **Yield Analytics**: Break-even analysis and time-to-maturity optimization

**Key Features:**
- Real Pendle market integration
- Conservative risk parameters (5% max allocation)
- Multi-layer yield opportunity scoring
- Portfolio health assessment

## API Integration

### Real Data Sources
- ✅ **Live Market Data**: Real-time price feeds and technical indicators
- ✅ **AI Analysis**: Claude API integration for intelligent reasoning
- ✅ **Technical Analysis**: RSI, Bollinger Bands, momentum indicators
- ✅ **DeFi Data**: Pendle yield farming opportunities, risk assessment
- ✅ **Risk Management**: Professional position sizing, portfolio allocation

### Unified API Endpoint
```
POST /api/virtuals/request
```

**Request Format:**
```json
{
  "agentId": "flow-yuki|flow-sakura|flow-ryu",
  "serviceName": "market_analysis|yield_optimization|token_analysis",
  "requestType": "analyze|execute",
  "payload": {"symbol": "BTC"},
  "requestId": "unique-request-id",
  "amount": 0.001,
  "userWallet": "0x..."
}
```

**Response Format:**
```json
{
  "request_id": "demo_request_...",
  "agent_id": "flow-yuki",
  "status": "success",
  "result": {
    "analysis": {
      "signal": {"direction": "LONG", "confidence": 0.6},
      "technical_analysis": {"rsi_14": 50.45, "trend": "sideways"},
      "ai_reasoning": "LONG signal with 60% confidence..."
    }
  },
  "transaction_hash": "0x..."
}
```

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/ayomidefagboyo/Floww-Virtuals-ACP.git
cd Floww-Virtuals-ACP
```

### 2. Setup Environment
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Server
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### 5. Test Agents

#### Test Yuki Agent (Trade Scanner)
```bash
curl -X POST "http://localhost:8001/api/virtuals/request" \
-H "Content-Type: application/json" \
-d '{
  "agentId": "flow-yuki",
  "serviceName": "market_analysis",
  "requestType": "analyze",
  "payload": {"symbol": "BTC"},
  "requestId": "test-001",
  "amount": 0.001,
  "userWallet": "0x1234..."
}'
```

#### Test Ryu Agent (Token Analysis)
```bash
curl -X POST "http://localhost:8001/api/virtuals/request" \
-H "Content-Type: application/json" \
-d '{
  "agentId": "flow-ryu",
  "serviceName": "token_analysis",
  "requestType": "analyze",
  "payload": {"symbol": "ETH"},
  "requestId": "test-002",
  "amount": 0.001,
  "userWallet": "0x1234..."
}'
```

#### Test Sakura Agent (Yield Farming)
```bash
curl -X POST "http://localhost:8001/api/virtuals/request" \
-H "Content-Type: application/json" \
-d '{
  "agentId": "flow-sakura",
  "serviceName": "yield_optimization",
  "requestType": "analyze",
  "payload": {},
  "requestId": "test-003",
  "amount": 0.001,
  "userWallet": "0x1234..."
}'
```

## Smart Contract Integration

### VirtualsACP Contract
- **Network**: Base Sepolia (Testnet)
- **Address**: Deployed via Foundry
- **Functions**: Request creation, agreement signing, service delivery
- **Payment**: ETH-based escrow system

### Contract Deployment
```bash
cd contracts
forge build
forge script script/DeployVirtualsACP.s.sol --rpc-url $ALCHEMY_RPC_URL --private-key $BACKEND_PRIVATE_KEY --broadcast
```

## Environment Variables

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=true

# Virtuals ACP Integration
VIRTUALS_ACP_CONTRACT_ADDRESS=0x...
ALCHEMY_RPC_URL=https://base-sepolia.g.alchemy.com/v2/...
BACKEND_PRIVATE_KEY=0x...
CHAIN_ID=84532

# AI Agent APIs
ANTHROPIC_API_KEY=sk-ant-...
HYPERLIQUID_TESTNET=true
```

## Agent Service Mapping

### Yuki Agent Services
- `market_analysis` + `analyze`: Live BTC/ETH technical analysis with AI reasoning
- `futures_trading` + `scan`: Market opportunity scanning with risk assessment
- `market_analysis` + `execute`: Trade execution analysis with position sizing

**Real Implementation Features:**
- Unified Signal Generator with 15+ technical indicators
- Claude API integration for AI reasoning
- Dynamic confidence scoring and risk assessment
- Professional signal formatting with price targets

### Ryu Agent Services
- `token_analysis` + `analyze`: Comprehensive token analysis cards
- `balanced_trading` + `scan`: Multi-token portfolio analysis
- `token_analysis` + `execute`: Trade execution with risk management

**Real Implementation Features:**
- Multi-factor scoring system (Technical, Fundamental, Momentum, Sentiment)
- Professional analysis card formatting
- Dynamic risk assessment and position sizing
- Alternative scenario planning with probabilities

### Sakura Agent Services
- `yield_optimization` + `analyze`: DeFi yield opportunity analysis
- `pendle_yield` + `scan`: Pendle protocol yield farming opportunities
- `yield_optimization` + `execute`: Yield strategy execution planning

**Real Implementation Features:**
- Pendle market integration with PT/YT analysis
- Conservative risk parameters with safety buffers
- Multi-asset portfolio allocation strategies
- Break-even analysis and yield optimization

## API Status Endpoints

### Agent List
```
GET /api/virtuals/agents
```
Returns available agents with pricing and services.

### Integration Status
```
GET /api/virtuals/status
```
Returns contract status, network info, and available services.

## Development

### Project Structure
```
Floww-Virtuals-ACP/
├── backend/
│   ├── app/
│   │   ├── api/virtuals/        # Virtuals API endpoints
│   │   ├── services/            # Agent implementations
│   │   │   ├── yuki_agent_service.py      # Trade Scanner
│   │   │   ├── ryu_agent_service.py       # Token Analysis
│   │   │   ├── sakura_agent_service.py    # Yield Farming
│   │   │   ├── virtuals_agent_router.py   # Request routing
│   │   │   └── virtuals_acp_service.py    # ACP protocol
│   │   └── config/              # Configuration
│   ├── requirements.txt
│   └── .env
├── contracts/
│   ├── src/VirtualsACP.sol     # Smart contract
│   ├── script/                  # Deployment scripts
│   └── foundry.toml
└── README.md
```

### Agent Implementation Details

Each agent service implements the complete floww3.0 functionality:

**Yuki Agent (yuki_agent_service.py):**
- Complete technical analysis with RSI, MACD, Bollinger Bands
- AI-powered signal generation with Claude API
- Market opportunity discovery and scoring
- Professional signal formatting with confidence levels

**Ryu Agent (ryu_agent_service.py):**
- Multi-factor analysis scoring system
- Professional token analysis card generation
- Dynamic risk assessment and position sizing
- Comprehensive market context analysis

**Sakura Agent (sakura_agent_service.py):**
- Pendle market integration with yield optimization
- Conservative risk management framework
- Portfolio allocation with diversification
- Real-time yield opportunity assessment

## Hackathon Submission

### Qualification Requirements
✅ **Agent Commerce Protocol**: 4-phase onchain protocol implemented
✅ **Base Network**: Deployed on Base Sepolia testnet
✅ **Functional Agents**: 3 working AI agents with real floww3.0 implementations
✅ **API Integration**: Unified REST API for agent interaction
✅ **Smart Contracts**: Solidity contracts with Foundry deployment
✅ **Real Data**: Live market data, technical analysis, AI reasoning

### Demo URLs
- **API Documentation**: `http://localhost:8001/docs`
- **Agent Status**: `http://localhost:8001/api/virtuals/status`
- **Available Agents**: `http://localhost:8001/api/virtuals/agents`

### Key Features
- **Onchain Agent Commerce**: Full ACP protocol implementation with ETH payments
- **Multi-Agent System**: 3 specialized trading agents with distinct strategies
- **Real AI Analysis**: Claude API integration for intelligent market insights
- **Live Market Data**: Real-time price feeds and comprehensive technical indicators
- **Professional Risk Management**: Advanced position sizing and portfolio allocation
- **Base Network Integration**: Native Base deployment with smart contract interaction

### Technical Excellence
- **Production-Ready Code**: Based on battle-tested floww3.0 implementations
- **Comprehensive Testing**: Full API endpoint coverage with real data validation
- **Professional Architecture**: Modular design with proper separation of concerns
- **Advanced Features**: Multi-factor analysis, yield optimization, AI reasoning

---

**Built for the Virtuals Ethereum AI Hackathon**
Flow AI Trading Platform - Bringing professional AI trading agents to the Virtuals ecosystem with real functionality and production-grade implementations.