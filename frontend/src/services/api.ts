import axios from 'axios';
import { Agent, TokenAnalysisResult, TradeScanResult, YieldAnalysisResult } from '@/types/agents';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  // Finite default timeout for normal requests (status, short analyses)
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const agentsService = {
  // Get all available agents
  async getAgents(): Promise<Agent[]> {
    try {
      const response = await api.get('/api/agents/status');

      // Transform backend agent data to frontend format
      const agents: Agent[] = Object.entries(response.data.agents).map(([key, agent]: [string, any]) => ({
        id: key,
        name: agent.name,
        description: agent.description,
        status: agent.status === 'online' ? 'online' as const : 'offline' as const,
        specialty: getSpecialtyFromCapabilities(agent.capabilities),
        actionLabel: getActionLabel(key),
        resultType: getResultType(key),
      }));

      return agents;
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      // Return default agents if API fails
      return getDefaultAgents();
    }
  },

  // Ryu Agent - Token Analysis
  async analyzeToken(symbol: string): Promise<TokenAnalysisResult> {
    try {
      console.log(`🔍 Requesting Ryu analysis for ${symbol}...`);

      const response = await api.post('/api/agents/ryu/analyze', {
        symbol: symbol.toUpperCase(),
        analysis_type: 'comprehensive'
      });

      const data = response.data;

      console.log(`✅ Ryu analysis completed for ${symbol}`);

      return {
        symbol: data.symbol,
        action: data.recommendation || 'HOLD',
        confidence: data.confidence || 0.5,
        currentPrice: data.current_price || 0,
        entryRange: {
          min: data.entry_levels?.entry_range_low || 0,
          max: data.entry_levels?.entry_range_high || 0,
        },
        targets: {
          target1: data.entry_levels?.target_1 || 0,
          target2: data.entry_levels?.target_2,
          target3: undefined,
        },
        stopLoss: data.entry_levels?.stop_loss || 0,
        riskRewardRatio: calculateRiskReward(
          data.current_price,
          data.entry_levels?.target_1,
          data.entry_levels?.stop_loss,
          data.recommendation
        ),
        analysis: {
          technical: `RSI: ${data.technical_analysis?.rsi_14?.toFixed(1) || 'N/A'}, MACD: ${data.technical_analysis?.macd_line?.toFixed(4) || 'N/A'}, Trend: ${data.technical_analysis?.trend || 'Unknown'}`,
          fundamental: `Market cap analysis and volume assessment completed`,
          sentiment: `Market sentiment: ${data.risk_assessment || 'Neutral'}`,
          risk: `Risk Level: ${data.risk_assessment || 'Medium'}`,
        },
        scores: {
          technical: data.scores?.technical || 75,
          fundamental: data.scores?.overall * 0.8 || 70,
          momentum: data.scores?.momentum || 65,
          sentiment: data.scores?.volume * 0.7 || 60,
          overall: data.scores?.overall || 68,
        },
        timestamp: data.timestamp || new Date().toISOString(),
      };
    } catch (error: any) {
      console.error('Token analysis failed:', error);

      // Handle specific API errors more gracefully
      if (error.response?.status === 404 && error.response?.data?.detail) {
        // Extract the meaningful error message from 404 responses
        throw new Error(error.response.data.detail);
      } else if (error.response?.data?.detail) {
        // Handle other API errors with detail messages
        throw new Error(error.response.data.detail);
      } else {
        // Fallback for network or other errors
        throw new Error(`Failed to analyze ${symbol}: ${error instanceof Error ? error.message : 'Network Error'}`);
      }
    }
  },

  // Yuki Agent - Trade Scanner
  async scanTrades(): Promise<TradeScanResult> {
    try {
      console.log('⚡ Requesting Yuki trade scan...');

      const response = await api.post(
        '/api/agents/yuki/scan',
        {
          scan_type: 'opportunities',
          pairs_limit: 500
        },
        {
          // Disable timeout only for long-running Yuki scans
          timeout: 0,
        }
      );

      const data = response.data;

      console.log(`✅ Yuki scan completed: ${data.opportunities_found} opportunities found`);

      return {
        opportunities: data.opportunities.map((opp: any) => ({
          id: opp.id,
          symbol: opp.symbol,
          direction: opp.direction,
          confidence: opp.confidence,
          entryPrice: opp.entry_price,
          target1: opp.target_1,
          target2: opp.target_2,
          stopLoss: opp.stop_loss,
          riskRewardRatio: opp.risk_reward_ratio,
          timeHorizon: opp.time_horizon,
          reasoning: opp.reasoning,
          keyFactors: opp.key_factors || [],
          expiresAt: opp.expires_at,
        })),
        totalScanned: data.total_scanned || 500,
        bestOpportunity: data.opportunities[0] || null,
        marketCondition: data.market_condition || 'Analyzed',
        timestamp: data.timestamp || new Date().toISOString(),
      };
    } catch (error) {
      console.error('Trade scanning failed:', error);
      throw new Error(`Failed to scan trades: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  // Yuki Agent - Progressive streaming scan (SSE)
  streamTrades(onEvent: (evt: { type: 'progress' | 'opportunity' | 'complete' | 'error'; data: any }) => void): () => void {
    const url = `${API_BASE_URL}/api/agents/yuki/scan/stream`;
    const es = new EventSource(url);

    const safeParse = (raw: any) => {
      try {
        if (typeof raw === 'string') return JSON.parse(raw);
        return raw;
      } catch {
        return raw;
      }
    };

    es.addEventListener('progress', (e: MessageEvent) => onEvent({ type: 'progress', data: safeParse(e.data) }));
    es.addEventListener('opportunity', (e: MessageEvent) => onEvent({ type: 'opportunity', data: safeParse(e.data) }));
    es.addEventListener('complete', (e: MessageEvent) => onEvent({ type: 'complete', data: safeParse(e.data) }));
    es.addEventListener('error', (e: MessageEvent) => onEvent({ type: 'error', data: safeParse((e as any).data || 'stream error') }));

    // Return unsubscribe function
    return () => es.close();
  },

  // Sakura Agent - Yield Opportunities
  async getYieldOpportunities(): Promise<YieldAnalysisResult> {
    try {
      console.log('🌸 Requesting Sakura yield analysis...');

      const response = await api.post('/api/agents/sakura/yield', {
        analysis_type: 'yield_farming',
        risk_preference: 'conservative'
      });

      const data = response.data;

      console.log(`✅ Sakura analysis completed: ${data.opportunities.length} yield opportunities found`);

      return {
        opportunities: data.opportunities.map((opp: any) => ({
          id: opp.id,
          protocol: opp.protocol,
          asset: opp.asset,
          apy: opp.apy,
          tvl: opp.tvl,
          riskLevel: opp.risk_level,
          maturity: opp.maturity,
          minimumDeposit: opp.minimum_deposit,
          strategy: opp.strategy,
          projectedReturns: opp.projected_returns,
        })),
        totalTvlAnalyzed: data.total_tvl_analyzed || 0,
        bestOpportunity: data.opportunities[0] || null,
        portfolioRecommendation: {
          allocation: data.portfolio_recommendation?.allocation?.map((alloc: any) => ({
            opportunity: {
              id: alloc.protocol.toLowerCase(),
              protocol: alloc.protocol,
              asset: 'Multi',
              apy: alloc.apy_contribution * (100 / alloc.percentage),
              tvl: 0,
              riskLevel: 'LOW' as const,
              minimumDeposit: 100,
              strategy: 'Portfolio Allocation',
              projectedReturns: {
                monthly: alloc.apy_contribution / 12,
                quarterly: alloc.apy_contribution / 4,
                yearly: alloc.apy_contribution,
              },
            },
            percentage: alloc.percentage,
          })) || [],
          totalProjectedApy: data.portfolio_recommendation?.total_projected_apy || 0,
          riskScore: data.portfolio_recommendation?.risk_score || 0.25,
        },
        timestamp: data.timestamp || new Date().toISOString(),
      };
    } catch (error) {
      console.error('Yield analysis failed:', error);
      throw new Error(`Failed to get yield opportunities: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  // Get integration status
  async getStatus() {
    try {
      const response = await api.get('/api/agents/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get status:', error);
      return null;
    }
  },
};

// Helper functions
function getSpecialtyFromCapabilities(capabilities: string[]): string {
  if (capabilities.includes('token_analysis')) return 'Token Analysis';
  if (capabilities.includes('market_scanning')) return 'Trade Scanner';
  if (capabilities.includes('yield_optimization')) return 'Yield Farming';
  return 'AI Analysis';
}

function getActionLabel(agentId: string): string {
  switch (agentId) {
    case 'ryu': return 'Analyze Token';
    case 'yuki': return 'Find Trades';
    case 'sakura': return 'Get Yield Opportunities';
    default: return 'Execute';
  }
}

function getResultType(agentId: string): string {
  switch (agentId) {
    case 'ryu': return 'AI Token Analysis Report';
    case 'yuki': return 'Market Opportunities';
    case 'sakura': return 'DeFi Yield Options';
    default: return 'Analysis Results';
  }
}

function getDefaultAgents(): Agent[] {
  return [
    {
      id: 'ryu',
      name: 'Ryu Agent',
      description: 'Professional token analysis with comprehensive AI scoring and risk assessment.',
      status: 'online',
      specialty: 'Token Analysis',
      actionLabel: 'Analyze Token',
      resultType: 'AI Token Analysis Report',
    },
    {
      id: 'yuki',
      name: 'Yuki Agent',
      description: 'Advanced trade scanner for high-frequency opportunities across 500+ trading pairs.',
      status: 'online',
      specialty: 'Trade Scanner',
      actionLabel: 'Find Trades',
      resultType: 'Market Opportunities',
    },
    {
      id: 'sakura',
      name: 'Sakura Agent',
      description: 'Conservative DeFi yield farming with Pendle integration and risk-adjusted returns.',
      status: 'online',
      specialty: 'Yield Farming',
      actionLabel: 'Get Yield Opportunities',
      resultType: 'DeFi Yield Options',
    },
  ];
}

function calculateRiskReward(entry: number, target: number, stop: number, direction: string): number {
  try {
    if (!entry || !target || !stop) return 0;

    let reward: number;
    let risk: number;

    if (direction === 'LONG') {
      reward = target - entry;
      risk = entry - stop;
    } else {
      reward = entry - target;
      risk = stop - entry;
    }

    if (risk <= 0) return 0;
    return reward / risk;
  } catch {
    return 0;
  }
}

export default api;