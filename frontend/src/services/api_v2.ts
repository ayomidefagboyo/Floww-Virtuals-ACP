import axios from 'axios';
import {
  Agent,
  AgentStatusResponse,
  TokenAnalysisResponse,
  TradeScanResponse,
  YieldAnalysisResponse,
  TokenAnalysisRequest,
  TradeScanRequest,
  YieldAnalysisRequest,
  HealthCheckResponse,
  StreamEvent
} from '@/types/agents_v2';

// Use Next.js rewrite proxy by default. If NEXT_PUBLIC_API_URL is set, it will override.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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

export const agentsServiceV2 = {
  // Get all available agents
  async getAgents(): Promise<Agent[]> {
    try {
      const response = await api.get<AgentStatusResponse>('/api/agents/status');

      // Transform backend agent data to frontend format
      const agents: Agent[] = Object.entries(response.data.agents).map(([key, agent]) => ({
        id: key,
        name: agent.name,
        description: agent.description,
        status: agent.status,
        specialty: getSpecialtyFromName(agent.name),
        actionLabel: getActionLabel(key),
        resultType: getResultType(key),
        capabilities: agent.capabilities,
        risk_level: agent.risk_level,
        last_activity: agent.last_activity,
      }));

      return agents;
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      // Return default agents if API fails
      return getDefaultAgents();
    }
  },

  // Ryu Agent - Token Analysis
  async analyzeToken(symbol: string): Promise<TokenAnalysisResponse> {
    try {
      console.log(`🔍 Requesting Ryu analysis for ${symbol}...`);

      const response = await api.post<TokenAnalysisResponse>('/api/agents/ryu/analyze', {
        symbol: symbol.toUpperCase(),
        analysis_type: 'comprehensive'
      });

      const data = response.data;

      // Check if the response contains an error
      if (data.status === 'error') {
        throw new Error(data.error || 'Analysis failed');
      }

      console.log(`✅ Ryu analysis completed for ${symbol}`);
      return data;
    } catch (error: any) {
      console.error('Token analysis failed:', error);
      throw new Error(`Failed to analyze ${symbol}: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Yuki Agent - Trade Scanner
  async scanTrades(): Promise<TradeScanResponse> {
    try {
      console.log('� Requesting Yuki trade scan...');

      const response = await api.post<TradeScanResponse>(
        '/api/agents/yuki/scan',
        {
          scan_type: 'opportunities',
          pairs_limit: 500
        },
        {
          timeout: 0, // No timeout for long-running scans
        }
      );

      const data = response.data;
      console.log(`✅ Yuki scan completed: ${data.opportunities_found} opportunities found`);
      return data;
    } catch (error: any) {
      console.error('Trade scanning failed:', error);
      throw new Error(`Failed to scan trades: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Yuki Agent - Progressive streaming scan (SSE)
  streamTrades(onEvent: (evt: StreamEvent) => void): () => void {
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

    es.addEventListener('progress', (e: MessageEvent) =>
      onEvent({ type: 'progress', data: safeParse(e.data) })
    );
    es.addEventListener('opportunity', (e: MessageEvent) =>
      onEvent({ type: 'opportunity', data: safeParse(e.data) })
    );
    es.addEventListener('complete', (e: MessageEvent) =>
      onEvent({ type: 'complete', data: safeParse(e.data) })
    );
    es.addEventListener('error', (e: MessageEvent) =>
      onEvent({ type: 'error', data: safeParse((e as any).data || 'stream error') })
    );

    // Return unsubscribe function
    return () => es.close();
  },

  // Sakura Agent - Yield Opportunities
  async getYieldOpportunities(investmentAmount: number = 10000): Promise<YieldAnalysisResponse> {
    try {
      console.log('🌸 Requesting Sakura yield analysis...');

      const response = await api.post<YieldAnalysisResponse>('/api/agents/sakura/yield', {
        analysis_type: 'yield_farming',
        risk_preference: 'conservative',
        investment_amount: investmentAmount
      });

      const data = response.data;
      console.log(`✅ Sakura analysis completed: ${data.opportunities?.length || 0} yield opportunities found`);

      return data;
    } catch (error: any) {
      console.error('Yield analysis failed:', error);
      throw new Error(`Failed to get yield opportunities: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Health check
  async getHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await api.get<HealthCheckResponse>('/api/agents/health');
      return response.data;
    } catch (error: any) {
      console.error('Health check failed:', error);
      throw new Error(`Health check failed: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Get status
  async getStatus(): Promise<AgentStatusResponse> {
    try {
      const response = await api.get<AgentStatusResponse>('/api/agents/status');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get status:', error);
      throw new Error(`Failed to get status: ${error.response?.data?.detail || error.message}`);
    }
  },
};

// Helper functions
function getSpecialtyFromName(name: string): string {
  if (name.includes('Token') || name.includes('Ryu')) return 'Token Analysis';
  if (name.includes('Scanner') || name.includes('Yuki')) return 'Market Scanner';
  if (name.includes('Yield') || name.includes('Sakura')) return 'Yield Farming';
  return 'AI Analysis';
}

function getActionLabel(agentId: string): string {
  switch (agentId) {
    case 'ryu': return 'Analyze Token';
    case 'yuki': return 'Scan Markets';
    case 'sakura': return 'Find Yields';
    default: return 'Execute';
  }
}

function getResultType(agentId: string): string {
  switch (agentId) {
    case 'ryu': return 'Token Analysis Report';
    case 'yuki': return 'Trading Opportunities';
    case 'sakura': return 'Yield Farming Options';
    default: return 'Analysis Results';
  }
}

function getDefaultAgents(): Agent[] {
  return [
    {
      id: 'ryu',
      name: 'Ryu Agent',
      description: 'Comprehensive token analysis with technical indicators',
      status: 'online',
      specialty: 'Token Analysis',
      actionLabel: 'Analyze Token',
      resultType: 'Token Analysis Report',
      capabilities: ['token_analysis', 'technical_indicators', 'risk_assessment'],
      risk_level: 'medium',
      last_activity: new Date().toISOString(),
    },
    {
      id: 'yuki',
      name: 'Yuki Agent',
      description: 'Real-time market scanning for trading opportunities',
      status: 'online',
      specialty: 'Market Scanner',
      actionLabel: 'Scan Markets',
      resultType: 'Trading Opportunities',
      capabilities: ['market_scanning', 'signal_generation', 'futures_analysis'],
      risk_level: 'high',
      last_activity: new Date().toISOString(),
    },
    {
      id: 'sakura',
      name: 'Sakura Agent',
      description: 'Conservative DeFi yield farming analysis',
      status: 'online',
      specialty: 'Yield Farming',
      actionLabel: 'Find Yields',
      resultType: 'Yield Farming Options',
      capabilities: ['yield_farming', 'defi_analysis', 'risk_assessment', 'portfolio_allocation'],
      risk_level: 'low',
      last_activity: new Date().toISOString(),
    },
  ];
}

export default api;