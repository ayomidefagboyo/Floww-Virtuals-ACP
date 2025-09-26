# Floww X Virtuals ACP Setup Guide

## Overview
This project recreates the full trading agent functionality from Flow/floww3.0 with real market data integration for Binance trading pairs, technical analysis, and yield farming opportunities.

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+
- npm or yarn

### API Requirements
- No API keys required for basic functionality (uses public Binance data)
- Optional: Anthropic API key for enhanced AI analysis

## Backend Setup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `backend/.env` file:
```
# Basic Configuration
PROJECT_NAME="Floww X Virtuals ACP"
VERSION="1.0.0"
DESCRIPTION="AI Trading Agents with Real Market Data"
HOST="0.0.0.0"
PORT=8001
DEBUG=true
LOG_LEVEL="INFO"

# Optional: Enhanced AI Analysis
ANTHROPIC_API_KEY=your_key_here  # Optional for advanced analysis
```

### 3. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Backend will be available at: http://localhost:8001

## Frontend Setup

### 1. Install Node Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 3. Start Frontend Development Server
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Agent Functionality

### Yuki Agent - Trade Scanner
- **Purpose**: Scans 500+ Binance trading pairs for opportunities
- **Features**: Real-time technical analysis, RSI/MACD/Bollinger Bands
- **Data Source**: Live Binance market data
- **Usage**: Click "Find Trades" to get best opportunities

### Ryu Agent - Token Analysis
- **Purpose**: Comprehensive token analysis with AI scoring
- **Features**: Technical indicators, risk assessment, entry/exit levels
- **Data Source**: Real Binance price/volume data
- **Usage**: Enter token symbol (e.g., BTC, ETH) for analysis

### Sakura Agent - Yield Opportunities
- **Purpose**: DeFi yield farming analysis with conservative strategies
- **Features**: Portfolio recommendations, risk-adjusted returns
- **Data Source**: Pendle, Aave, Compound protocols
- **Usage**: Click "Get Yield Opportunities" for DeFi strategies

## Testing Agent Functionality

### 1. Test Yuki Trade Scanner
```bash
curl -X POST http://localhost:8001/api/agents/yuki/scan \
  -H "Content-Type: application/json" \
  -d '{"scan_type": "opportunities", "pairs_limit": 500}'
```

### 2. Test Ryu Token Analysis
```bash
curl -X POST http://localhost:8001/api/agents/ryu/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "analysis_type": "comprehensive"}'
```

### 3. Test Sakura Yield Analysis
```bash
curl -X POST http://localhost:8001/api/agents/sakura/yield \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "yield_farming", "risk_preference": "conservative"}'
```

## Troubleshooting

### Common Issues

1. **Rate Limiting Errors**
   - Binance API has rate limits (1200 requests/minute)
   - Built-in rate limiting handles this automatically
   - Wait 1 minute if you see rate limit errors

2. **Missing Dependencies**
   - Ensure all requirements.txt packages are installed
   - For TA-Lib issues on Mac: `brew install ta-lib`
   - For TA-Lib issues on Linux: Install ta-lib development packages

3. **CORS Issues**
   - Backend allows all origins by default
   - Ensure frontend API_URL matches backend address

4. **Network Connectivity**
   - Agents require internet access for Binance API
   - Check firewall settings if connection fails

### Logs and Debugging

Backend logs show detailed agent activity:
- Yuki scan progress: "🔍 Yuki starting comprehensive market scan..."
- Ryu analysis: "📊 Ryu token analysis requested for: BTC"
- API errors: "Error in [agent] analysis: [details]"

## Architecture Notes

- **Real Data Integration**: All agents use live market data, not mock responses
- **Rate Limiting**: Built-in protection against API limits
- **Error Handling**: Comprehensive error handling with fallbacks
- **Performance**: Optimized for handling 500+ trading pairs
- **Security**: No sensitive data stored, public APIs only

## Development Notes

This implementation completely recreates the Flow/floww3.0 trading functionality with:
- Real Binance market data integration
- Technical analysis with multiple indicators
- Sophisticated opportunity scoring algorithms
- Production-ready error handling and rate limiting

All agents are now functional with real market data instead of dummy responses.