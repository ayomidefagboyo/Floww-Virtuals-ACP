#!/bin/bash

# Floww Virtuals ACP - Functional Agent API Examples
# Updated for real agent implementations with working functionality

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL (update this to your deployed backend URL)
BASE_URL="http://localhost:8001"

echo -e "${BLUE}🚀 Floww Virtuals ACP - Functional Agent API Examples${NC}"
echo "====================================================="
echo ""

# 1. Health check
echo -e "${GREEN}1. Health Check${NC}"
echo "GET $BASE_URL/"
curl -X GET "$BASE_URL/" 2>/dev/null | jq . || echo "API endpoint available"
echo ""
echo ""

# 2. Get available agents
echo -e "${GREEN}2. Available Agents${NC}"
echo "GET $BASE_URL/api/virtuals/agents"
curl -X GET "$BASE_URL/api/virtuals/agents" 2>/dev/null | jq .
echo ""
echo ""

# 3. Get integration status
echo -e "${GREEN}3. Integration Status${NC}"
echo "GET $BASE_URL/api/virtuals/status"
curl -X GET "$BASE_URL/api/virtuals/status" 2>/dev/null | jq .
echo ""
echo ""

# 4. Yuki Agent - Market Analysis (Trade Scanner)
echo -e "${GREEN}4. Yuki Agent - Market Analysis (BTC Trade Scanner)${NC}"
echo -e "${YELLOW}   Real Implementation: Unified Signal Generator with AI reasoning${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "analyze",
    "payload": {
      "symbol": "BTC"
    },
    "requestId": "yuki_btc_analysis_001",
    "amount": 0.001,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 5. Yuki Agent - Trade Execution
echo -e "${GREEN}5. Yuki Agent - Trade Execution Analysis${NC}"
echo -e "${YELLOW}   Real Implementation: Position sizing and execution planning${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "execute",
    "payload": {
      "symbol": "BTC"
    },
    "requestId": "yuki_btc_execute_001",
    "amount": 0.001,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 6. Ryu Agent - Token Analysis Card (ETH)
echo -e "${GREEN}6. Ryu Agent - Token Analysis Card (ETH)${NC}"
echo -e "${YELLOW}   Real Implementation: Professional analysis cards with multi-factor scoring${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-ryu",
    "serviceName": "token_analysis",
    "requestType": "analyze",
    "payload": {
      "symbol": "ETH",
      "risk_tolerance": "medium",
      "time_horizon": "medium"
    },
    "requestId": "ryu_eth_analysis_001",
    "amount": 0.001,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 7. Ryu Agent - Multi-Token Scan
echo -e "${GREEN}7. Ryu Agent - Multi-Token Portfolio Scan${NC}"
echo -e "${YELLOW}   Real Implementation: Balanced trading analysis across multiple assets${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-ryu",
    "serviceName": "balanced_trading",
    "requestType": "scan",
    "payload": {
      "symbols": ["ETH", "BTC", "SOL"],
      "risk_tolerance": "medium"
    },
    "requestId": "ryu_portfolio_scan_001",
    "amount": 0.001,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 8. Sakura Agent - Yield Optimization Analysis
echo -e "${GREEN}8. Sakura Agent - Yield Optimization Analysis${NC}"
echo -e "${YELLOW}   Real Implementation: Pendle yield farming with portfolio allocation${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-sakura",
    "serviceName": "yield_optimization",
    "requestType": "analyze",
    "payload": {},
    "requestId": "sakura_yield_analysis_001",
    "amount": 0.0005,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 9. Sakura Agent - Pendle Market Scan
echo -e "${GREEN}9. Sakura Agent - Pendle Market Scan${NC}"
echo -e "${YELLOW}   Real Implementation: Conservative DeFi yield farming opportunities${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-sakura",
    "serviceName": "pendle_yield",
    "requestType": "scan",
    "payload": {
      "focus_assets": ["ETH", "USDC", "stETH"]
    },
    "requestId": "sakura_pendle_scan_001",
    "amount": 0.0005,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .
echo ""
echo ""

# 10. Sakura Agent - Yield Strategy Execution
echo -e "${GREEN}10. Sakura Agent - Yield Strategy Execution${NC}"
echo -e "${YELLOW}    Real Implementation: Yield strategy execution with risk management${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-sakura",
    "serviceName": "yield_optimization",
    "requestType": "execute",
    "payload": {},
    "requestId": "sakura_yield_execute_001",
    "amount": 0.0005,
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' 2>/dev/null | jq .

echo ""
echo -e "${BLUE}✅ Functional Agent API examples completed!${NC}"
echo ""
echo -e "${YELLOW}🔥 Key Features Demonstrated:${NC}"
echo "• Yuki: Real trade scanner with AI reasoning and technical analysis"
echo "• Ryu: Professional token analysis cards with multi-factor scoring"
echo "• Sakura: Pendle yield farming integration with portfolio optimization"
echo "• All agents use real market data and AI-powered analysis"
echo "• Production-ready implementations from floww3.0 codebase"