#!/bin/bash

# Floww Virtuals ACP - Example API calls

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL (update this to your deployed backend URL)
BASE_URL="http://localhost:8000"

echo -e "${BLUE}🚀 Floww Virtuals ACP - Example API Calls${NC}"
echo "=============================================="
echo ""

# 1. Health check
echo -e "${GREEN}1. Health Check${NC}"
echo "GET $BASE_URL/"
curl -X GET "$BASE_URL/" | jq .
echo ""
echo ""

# 2. Get available agents
echo -e "${GREEN}2. Available Agents${NC}"
echo "GET $BASE_URL/api/virtuals/agents"
curl -X GET "$BASE_URL/api/virtuals/agents" | jq .
echo ""
echo ""

# 3. Get integration status
echo -e "${GREEN}3. Integration Status${NC}"
echo "GET $BASE_URL/api/virtuals/status"
curl -X GET "$BASE_URL/api/virtuals/status" | jq .
echo ""
echo ""

# 4. Example analyze request (Yuki market analysis)
echo -e "${GREEN}4. Analyze Request - Yuki Market Analysis${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-yuki",
    "serviceName": "market_analysis",
    "requestType": "analyze",
    "payload": {
      "symbol": "ETH/USD",
      "timeframe": "1h",
      "indicators": ["RSI", "MACD", "Bollinger Bands"]
    },
    "requestId": "req_yuki_analyze_001",
    "amount": 0.001,
    "currency": "ETH",
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' | jq .
echo ""
echo ""

# 5. Example execute request (Sakura yield optimization)
echo -e "${GREEN}5. Execute Request - Sakura Yield Optimization${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-sakura",
    "serviceName": "yield_optimization",
    "requestType": "execute",
    "payload": {
      "amount": 1000,
      "token": "USDC",
      "strategy": "conservative",
      "max_risk": 0.05
    },
    "requestId": "req_sakura_execute_001",
    "amount": 0.0005,
    "currency": "ETH",
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' | jq .
echo ""
echo ""

# 6. Example execute request (Ryu balanced trading)
echo -e "${GREEN}6. Execute Request - Ryu Balanced Trading${NC}"
echo "POST $BASE_URL/api/virtuals/request"
curl -X POST "$BASE_URL/api/virtuals/request" \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "flow-ryu",
    "serviceName": "balanced_trading",
    "requestType": "execute",
    "payload": {
      "symbol": "BTC/USD",
      "side": "buy",
      "amount": 0.1,
      "type": "market"
    },
    "requestId": "req_ryu_execute_001",
    "amount": 0.0005,
    "currency": "ETH",
    "userWallet": "0x1234567890123456789012345678901234567890"
  }' | jq .

echo ""
echo -e "${BLUE}✅ API calls completed!${NC}"